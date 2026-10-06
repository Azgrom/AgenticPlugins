"""Offline package checks and fixture tests for the JSON Schema keywords used here.

This portable validator is intentionally a subset, not a general Draft 2020-12
implementation. Unknown keywords fail closed. It does not authenticate sources,
run a tutor model, migrate live state, or test activation in the ChatGPT host.
"""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
import argparse
import hashlib
import json
import re
import sys
import zipfile

SUPPORTED = {'$schema', '$id', '$defs', '$ref', 'title', 'description', 'type',
             'properties', 'required', 'additionalProperties', 'enum', 'const',
             'anyOf', 'allOf', 'not', 'if', 'then', 'items', 'minItems',
             'uniqueItems', 'minLength', 'minimum', 'maximum',
             'exclusiveMinimum', 'format'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_schema_shape(schema):
    assert isinstance(schema, dict), 'Schema must be an object'
    assert not set(schema) - SUPPORTED, f'Unsupported keywords: {set(schema) - SUPPORTED}'
    for key in ('anyOf', 'allOf'):
        for child in schema.get(key, []):
            check_schema_shape(child)
    for key in ('not', 'if', 'then', 'items'):
        if key in schema:
            check_schema_shape(schema[key])
    for key in ('properties', '$defs'):
        for child in schema.get(key, {}).values():
            check_schema_shape(child)


def validate(value, schema, base):
    """Check only the explicit keywords in SUPPORTED; no network resolution."""
    if '$ref' in schema:
        resource, _, pointer = schema['$ref'].partition('#')
        assert '://' not in resource, 'Remote references are not supported'
        ref_path = (base.parent / resource).resolve() if resource else base
        root = load(ref_path)
        target = root
        for segment in pointer.lstrip('/').split('/') if pointer else []:
            target = target[segment.replace('~1', '/').replace('~0', '~')]
        validate(value, target, ref_path)
    if 'const' in schema:
        assert type(value) is type(schema['const']) and value == schema['const'], 'Wrong const'
    if 'enum' in schema:
        assert any(type(value) is type(v) and value == v for v in schema['enum']), 'Wrong enum'
    if 'anyOf' in schema:
        assert any(matches(value, v, base) for v in schema['anyOf']), 'No anyOf branch matched'
    for branch in schema.get('allOf', []):
        validate(value, branch, base)
    if 'not' in schema:
        assert not matches(value, schema['not'], base), 'Forbidden value'
    if 'if' in schema and matches(value, schema['if'], base):
        validate(value, schema.get('then', {}), base)
    if 'type' in schema:
        checks = {'object': isinstance(value, dict), 'array': isinstance(value, list),
                  'string': isinstance(value, str), 'null': value is None,
                  'boolean': type(value) is bool,
                  'number': type(value) in (int, float),
                  'integer': type(value) is int}
        assert checks[schema['type']], f'Wrong type: {schema["type"]}'
    if isinstance(value, dict):
        assert set(schema.get('required', [])) <= set(value), 'Missing required properties'
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            assert set(value) <= set(props), 'Additional properties'
        for key, v in value.items():
            if key in props:
                validate(v, props[key], base)
    if isinstance(value, list):
        assert len(value) >= schema.get('minItems', 0), 'Too few items'
        if schema.get('uniqueItems'):
            assert len({json.dumps(v, sort_keys=True) for v in value}) == len(value), 'Duplicate items'
        if 'items' in schema:
            for v in value:
                validate(v, schema['items'], base)
    if isinstance(value, str):
        assert len(value) >= schema.get('minLength', 0), 'String too short'
        if schema.get('format') == 'date-time':
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            assert 'T' in value and dt.tzinfo is not None, 'Date-time needs timezone'
    if type(value) in (int, float):
        assert value >= schema.get('minimum', float('-inf')), 'Below minimum'
        assert value <= schema.get('maximum', float('inf')), 'Above maximum'
        assert value > schema.get('exclusiveMinimum', float('-inf')), 'Below exclusive minimum'


def matches(value, schema, base):
    try:
        validate(value, schema, base)
        return True
    except (AssertionError, ValueError):
        return False


def validate_bundle(records):
    """Validate a supplied, recoverable record set; never infer an external store.

    The six primary records can be supplemented by item_records, event_history,
    and evidence_records. Each ID must resolve inside this explicit record set.
    Passing these checks does not authenticate the content of a source.
    """
    profile = records['exam_profile']
    context = profile['context']['exam_key']
    profile_version = profile['profile_version']
    schema_dir = Path(__file__).resolve().parent.parent / 'references/schemas'

    def registry(primary, extra, id_field):
        values = [records[primary], *records.get(extra, [])]
        ids = [v[id_field] for v in values]
        assert len(ids) == len(set(ids)), f'Duplicate {id_field}'
        path = schema_dir / f'{primary}.schema.json'
        for value in values:
            validate(value, load(path), path)
        return dict(zip(ids, values))

    items = registry('item_record', 'item_records', 'item_id')
    events = registry('assessment_event', 'event_history', 'event_id')
    evidence = registry('evidence_record', 'evidence_records', 'evidence_id')
    superseded = {event['supersedes_event_id'] for event in events.values()
                  if event['supersedes_event_id'] is not None}
    for kind in ('item_record', 'assessment_event', 'student_state'):
        assert records[kind]['exam_key'] == context, 'Mixed exam contexts'
        assert records[kind]['profile_version'] == profile_version, 'Mixed profile versions'
    checkpoint = records['session_checkpoint']
    assert checkpoint['context'] == profile['context'], 'Checkpoint context differs from profile'
    assert checkpoint['profile_version'] == profile_version, 'Checkpoint version mismatch'
    assert set(records['student_state']['applied_event_ids']) <= set(events), 'Unresolved event ID'
    assert set(checkpoint['event_refs']) <= set(events), 'Unresolved checkpoint event'
    assert set(checkpoint['state_refs']) <= {records['student_state']['domain_id']}, 'Unresolved checkpoint state'
    assert set(records['student_state']['evidence_ids']) <= set(evidence), 'Unresolved state evidence'

    sources = [*profile['source_ids'], *profile['scoring']['source_ids']]
    sources += [v['source_id'] for v in profile['scoring']['minimum_rules']]
    sources += [v['source_id'] for v in profile['scoring']['component_weights']]
    for item in items.values():
        assert item['exam_key'] == context and item['profile_version'] == profile_version, 'Mixed item context'
        sources += item['source_ids']
    assert set(sources) <= set(evidence), 'Unresolved source ID'
    if profile['status'] == 'verified':
        for source_id in profile['source_ids']:
            source = evidence[source_id]
            assert source['claim_class'] == 'EXTERNAL_FACT' and source['origin'] == 'external' and source['confidence'] == 'verified', 'Profile source is not verified external evidence'
    for source in evidence.values():
        assert set(source['basis_ids']) <= set(evidence), 'Unresolved evidence basis'
        assert source['evidence_id'] not in source['basis_ids'], 'Evidence refers to itself'

    for event in events.values():
        assert event['exam_key'] == context and event['profile_version'] == profile_version, 'Mixed event context'
        assert set(event['item_ids']) <= set(items), 'Unresolved item ID'
        assert set(event['evidence_ids']) <= set(evidence), 'Unresolved event evidence'
        assert set(event['derived_from_event_ids']) <= set(events), 'Unresolved derived event'
        assert event['event_id'] not in event['derived_from_event_ids'], 'Event derives from itself'
        predecessor = event['supersedes_event_id']
        if predecessor is not None:
            assert event['event_kind'] == 'CORRECTION', 'Replacement is not a correction'
            assert predecessor in events, 'Unresolved original event'
            assert predecessor != event['event_id'], 'Correction refers to itself'
            original = events[predecessor]
            assert set(event['item_ids']) == set(original['item_ids']), 'Correction changes assessed items'
        types = {items[item_id]['material_type'] for item_id in event['item_ids']}
        if types:
            expected_type = next(iter(types)) if len(types) == 1 else None
            assert event['material_type'] == expected_type, 'Event material provenance differs from items'
            if len(types) > 1:
                assert event['event_kind'] == 'SUMMARY' and event['derived_from_event_ids'], 'Mixed origins require an explicit summary'
        if event['event_kind'] == 'SUMMARY':
            assert event['derived_from_event_ids'], 'Summary lacks source events'
            derived_types = {events[v]['material_type'] for v in event['derived_from_event_ids']}
            if len(derived_types) > 1:
                assert event['material_type'] is None, 'Mixed summary claims one origin'
        metric = event['metric']
        if metric['official']:
            assert event['event_kind'] in ('OFFICIAL_RESULT', 'CORRECTION') and event['origin'] == 'external', 'Local calculation is not an official result'
            assert not event['item_ids'], 'Official result is an external report, not local item scoring'
            assert event['evidence_ids'] and all(evidence[v]['claim_class'] == 'EXTERNAL_FACT' and evidence[v]['origin'] == 'external' and evidence[v]['confidence'] == 'verified' for v in event['evidence_ids']), 'Official result lacks verified external source'
            if predecessor is not None:
                assert events[predecessor]['metric']['official'], 'Official correction replaces a local result'
        if metric['kind'] == 'raw_accuracy':
            assert metric['numerator'] <= metric['denominator'], 'Numerator above denominator'
            assert metric['value'] is not None, 'Accuracy not supplied'
            assert abs(metric['value'] - metric['numerator'] / metric['denominator']) < 1e-9, 'Wrong accuracy ratio'
        if event['eligible_for_mastery'] and event['event_id'] not in superseded:
            assert event['item_ids'], 'Mastery event lacks assessed items'
            assert all(items[v]['eligibility'] == 'ACCEPT' for v in event['item_ids']), 'Ineligible item counted for mastery'

    def visit(event_id, stack, complete):
        assert event_id not in stack, 'Cyclic event history'
        if event_id in complete:
            return
        event = events[event_id]
        dependencies = event['derived_from_event_ids'] + ([event['supersedes_event_id']] if event['supersedes_event_id'] else [])
        for dependency in dependencies:
            visit(dependency, stack | {event_id}, complete)
        complete.add(event_id)

    complete = set()
    for event_id in events:
        visit(event_id, set(), complete)
    applied = set(records['student_state']['applied_event_ids'])
    assert not applied & superseded, 'Superseded event counted in current state'
    for event_id in applied:
        predecessor = events[event_id]['supersedes_event_id']
        while predecessor:
            assert predecessor not in applied, 'Original and correction both counted'
            predecessor = events[predecessor]['supersedes_event_id']


def resolve_link(file, target, skill):
    """Markdown paths are relative to the document containing them."""
    resolved = (file.parent / target.partition('#')[0]).resolve()
    assert resolved.is_relative_to(skill.resolve()), f'Link leaves skill: {file} → {target}'
    assert resolved.is_file(), f'Broken link: {file} → {target}'
    return resolved


def validate_academic_review(review, schema_path=None):
    """Check a supplied scholarly review without exam/student/store records.

    Links and access levels are checked; source authenticity and the semantic
    adequacy of a conclusion still require inspection by the consuming tutor.
    """
    schema_path = schema_path or Path(__file__).resolve().parent.parent / 'references/schemas/academic_review.schema.json'
    schema = load(schema_path)
    check_schema_shape(schema)
    validate(review, schema, schema_path)
    source_ids = [s['source_id'] for s in review['sources']]
    claim_ids = [c['claim_id'] for c in review['claims']]
    assert len(source_ids) == len(set(source_ids)), 'Duplicate academic source ID'
    assert len(claim_ids) == len(set(claim_ids)), 'Duplicate academic claim ID'
    sources = dict(zip(source_ids, review['sources']))
    scope = review['search_scope']
    if scope['kind'] != 'provided_material':
        assert scope['queries'] and scope['venues'] and scope['searched_at'], 'Search scope is not recoverable'
    if scope['kind'] == 'systematic':
        assert scope['limitations'], 'Systematic review needs a documented scope/process'
    for source in sources.values():
        if source['integrity_status'] != 'NOT_CHECKED':
            assert source['status_check_ref'] and source['status_checked_at'], 'Editorial status lacks an actual check'
    for claim in review['claims']:
        relations = set()
        for link in claim['links']:
            assert link['source_id'] in sources, 'Unresolved academic source ID'
            source = sources[link['source_id']]
            basis = link['basis']
            if basis == 'INSPECTED_TEXT':
                assert source['reading_level'] in ('EXCERPT', 'FULL_TEXT'), 'Metadata or abstract is not inspected body text'
                assert source['source_ref'] and link['locator'], 'Inspected text needs a source and locator'
            elif basis == 'ABSTRACT_REPORTED':
                assert source['reading_level'] in ('ABSTRACT', 'EXCERPT', 'FULL_TEXT'), 'Abstract was not read'
                assert source['source_ref'] and link['locator'], 'Abstract needs a source and locator'
            elif basis == 'METADATA':
                assert source['reading_level'] != 'NONE' and source['source_ref'], 'Metadata was not actually consulted'
                assert link['relation'] == 'context', 'Metadata cannot support or contradict a scholarly content claim'
            elif basis == 'UNVERIFIED':
                assert link['relation'] == 'context', 'Uninspected content cannot support or contradict a scholarly claim'
            if source['integrity_status'] == 'RETRACTED' and link['relation'] == 'supports':
                assert claim['limitations'], 'Retracted source supports an unqualified claim'
            relations.add(link['relation'])
        if claim['verdict'] == 'supported':
            assert 'supports' in relations, 'Supported claim has no supporting evidence'
        elif claim['verdict'] == 'contradicted':
            assert 'contradicts' in relations, 'Contradicted claim has no contrary evidence'
        elif claim['verdict'] == 'partially_supported':
            assert 'supports' in relations, 'Partial conclusion lacks supporting evidence'
    return True


def dated_citations(skill):
    """Informational inventory of 'consultado em' dates; staleness is reported, never enforced."""
    found = []
    for file in sorted((skill / 'references').rglob('*.md')):
        for number, line in enumerate(file.read_text(encoding='utf-8').splitlines(), 1):
            if 'consult' not in line.lower():
                continue
            for text in re.findall(r'\b\d{4}-\d{2}-\d{2}\b', line):
                try:
                    datetime.strptime(text, '%Y-%m-%d')
                except ValueError:
                    raise AssertionError(f'Invalid citation date {text} in {file.relative_to(skill)}:{number}')
                found.append((str(file.relative_to(skill)), number, text))
    return found


def run(skill, baseline=None):
    checks = 0
    plugin = skill.parent.parent
    core = skill / 'references/CORE.md'
    assert core.is_file(), 'Missing modular CORE'
    entry = (skill / 'SKILL.md').read_text()
    assert entry.startswith('---\n') and '\nname: instructions\n' in entry, 'Wrong skill frontmatter'
    assert len(entry.split()) < 650, 'Entry point too large'
    assert len(core.read_text().split()) < 800, 'CORE too large'
    checks += 3
    for file in skill.rglob('*.md'):
        body = file.read_text()
        assert len(re.findall(r'^\s*```', body, re.M)) % 2 == 0, f'Open fence: {file}'
        assert not re.search(r'\b(?:TODO|TBD|FIXME)\b', body), f'Placeholder: {file}'
        for target in re.findall(r'\[[^\]\n]+\]\(([^)]+)\)', body):
            if target.startswith(('http://', 'https://', '#')):
                continue
            resolve_link(file, target, skill)
            checks += 1
        checks += 1
    for file in skill.rglob('*.json'):
        load(file)
        checks += 1
    index = load(skill / 'lookup/knowledge-index.json')
    paths = [v['path'] for v in index['files']]
    assert len(paths) == len(set(paths)), 'Duplicate index paths'
    for path in paths:
        assert not path.endswith('.zip'), 'Legacy ZIP still active'
        assert (skill / path).is_file(), f'Unresolvable index: {path}'
        checks += 1
    inventory = {str(f.relative_to(skill)) for f in (skill / 'references').rglob('*')
                 if f.is_file() and f.suffix in ('.md', '.json')}
    assert inventory == set(paths), 'Index inventory incomplete'
    checks += 1
    root = load(plugin / 'plugin.json')
    overlay = load(plugin / '.codex-plugin/plugin.json')
    interface = root['extensions']['com.openai']['interface']
    assert len(interface['shortDescription']) <= 30, 'Subtitle above 30 chars'
    assert root['name'] == overlay['name'] and root['version'] == overlay['version'], 'Manifest mismatch'
    assert interface == overlay['interface'], 'Interface mismatch'
    assert re.fullmatch(r'\d+\.\d+\.\d+', root['version']), 'Version must be strict semver'
    # The manifest name is a platform-assigned ID; the checkout folder name is not constrained.
    assert sorted(str(f.relative_to(plugin)) for f in plugin.glob('skills/*/SKILL.md')) == ['skills/instructions/SKILL.md'], 'Discovered skill set changed'
    for key in ('logo', 'composerIcon'):
        assert (plugin / interface[key]).is_file(), f'Missing {key}'
    checks += 8
    if baseline:
        old = load(baseline / '.codex-plugin/plugin.json')
        assert root['name'] == old['name'] and root['author'] == old['author'], 'Identity lost'
        assert interface['defaultPrompt'] == old['interface']['defaultPrompt'], 'Prompt value changed'
        assert type(interface['defaultPrompt']) is type(old['interface']['defaultPrompt']), 'Prompt type changed'
        assert interface['capabilities'] == old['interface']['capabilities'], 'Capabilities changed'
        assert root['extensions']['com.openai'].keys() == {'interface'}, 'Unexpected app integration'
        for key in ('logo', 'composerIcon'):
            original = baseline / old['interface'][key]
            current = plugin / interface[key]
            assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(current.read_bytes()).digest(), 'Asset changed'
        checks += 7
    with zipfile.ZipFile(skill / 'references/instructions.zip') as archive:
        assert archive.namelist() == ['LEGACY.md'], 'Conflicting legacy knowledge remains'
        assert 'não contém regras ativas' in archive.read('LEGACY.md').decode(), 'Unclear legacy status'
    checks += 2
    records = {}
    schema_paths = {}
    for file in sorted((skill / 'references/schemas').glob('*.schema.json')):
        schema = load(file)
        check_schema_shape(schema)
        assert schema['$schema'] == 'https://json-schema.org/draft/2020-12/schema'
        record = load(skill / 'references/evals/fixtures' / file.name.replace('.schema', ''))
        validate(record, schema, file)
        name = file.name.removesuffix('.schema.json')
        records[name] = record
        schema_paths[name] = file
        checks += 2
    assert set(records) == {'academic_review', 'assessment_event', 'evidence_record', 'exam_profile', 'item_record', 'session_checkpoint', 'student_state'}, 'Wrong contract inventory'
    validate_bundle(records)
    academic_path = schema_paths['academic_review']
    validate_academic_review(records['academic_review'], academic_path)
    academic_negatives = [
        ('orphan_academic_source', lambda r: r['claims'][0]['links'][0].update(source_id='missing')),
        ('metadata_as_inspected_text', lambda r: r['sources'][0].update(reading_level='METADATA_ONLY')),
        ('abstract_as_inspected_text', lambda r: r['sources'][0].update(reading_level='ABSTRACT')),
        ('academic_locator_missing', lambda r: r['claims'][0]['links'][0].update(locator=None)),
        ('academic_source_missing', lambda r: r['sources'][0].update(source_ref=None)),
        ('unchecked_no_notice', lambda r: r['sources'][0].update(integrity_status='NO_NOTICE_FOUND')),
        ('duplicate_academic_source', lambda r: r['sources'].append(deepcopy(r['sources'][0]))),
        ('duplicate_academic_claim', lambda r: r['claims'].append(deepcopy(r['claims'][0]))),
        ('unrecorded_search', lambda r: r['search_scope'].update(kind='targeted')),
        ('unsupported_content_claim', lambda r: r['claims'][0].update(verdict='supported', links=[])),
        ('metadata_supports_content', lambda r: r['claims'][0]['links'][0].update(basis='METADATA')),
        ('unread_metadata', lambda r: (r['sources'][0].update(reading_level='NONE'), r['claims'][0].update(verdict='unresolved'), r['claims'][0]['links'][0].update(basis='METADATA', relation='context'))),
        ('contrary_evidence_as_partial_support', lambda r: r['claims'][0].update(verdict='partially_supported')),
    ]
    for label, mutate in academic_negatives:
        review = deepcopy(records['academic_review'])
        mutate(review)
        try:
            validate_academic_review(review, academic_path)
        except (AssertionError, ValueError):
            checks += 1
        else:
            raise AssertionError(f'Academic negative accepted: {label}')
    abstract_review = deepcopy(records['academic_review'])
    abstract_review['sources'][0]['reading_level'] = 'ABSTRACT'
    abstract_review['claims'][0]['links'][0].update(basis='ABSTRACT_REPORTED', locator='Resumo')
    validate_academic_review(abstract_review, academic_path)
    checks += 2
    checks += 2
    # Mutations target actual failures in record integrity rather than expected text.
    negatives = [
        ('external_fact_without_source', 'evidence_record', lambda r: r.update(claim_class='EXTERNAL_FACT', confidence='verified')),
        ('false_verified_profile', 'exam_profile', lambda r: r.update(status='verified')),
        ('past_without_occurrence', 'item_record', lambda r: r.update(material_type='OFFICIAL_PAST')),
        ('restricted_item', 'item_record', lambda r: r.update(rights_status='restricted')),
        ('restricted_training', 'item_record', lambda r: r.update(rights_status='restricted', eligibility='TRAINING_ONLY')),
        ('annulled_item_accepted', 'item_record', lambda r: r.update(annulled=True)),
        ('authorial_as_official', 'item_record', lambda r: r.update(answer_status='official')),
        ('unknown_origin_accepted', 'item_record', lambda r: r.update(material_type='USER_PROVIDED')),
        ('correction_without_original', 'assessment_event', lambda r: r.update(event_kind='CORRECTION')),
        ('answer_after_solution_as_mastery', 'assessment_event', lambda r: r.update(assistance='EXPLANATION_AFTER_ANSWER')),
        ('uncalibrated_scaled_estimate', 'assessment_event', lambda r: (r.update(origin='inferred'), r['metric'].update(kind='scaled_score', calibration='unavailable'))),
        ('domain_without_evidence', 'student_state', lambda r: r.update(state='A')),
        ('duplicate_applied_event', 'student_state', lambda r: r['applied_event_ids'].append('fixture.event')),
        ('personal_data_in_checkpoint', 'session_checkpoint', lambda r: r.update(student_name='unnecessary')),
        ('unknown_checkpoint_version', 'session_checkpoint', lambda r: r.update(checkpoint_version='99.0')),
        ('local_result_as_official', 'assessment_event', lambda r: r['metric'].update(official=True)),
        ('minimum_without_scale', 'exam_profile', lambda r: r['scoring']['minimum_rules'].append({'component':'A','minimum':60,'source_id':'fixture.evidence'})),
        ('nonpositive_weight', 'exam_profile', lambda r: r['scoring']['component_weights'].append({'component':'A','weight':0,'unit':'scale 0–100','source_id':'fixture.evidence'})),
    ]
    for label, name, mutate in negatives:
        record = deepcopy(records[name])
        mutate(record)
        assert not matches(record, load(schema_paths[name]), schema_paths[name]), f'Negative accepted: {label}'
        checks += 1
    bundle_negatives = [
        ('mixed_exam', lambda r: r['assessment_event'].update(exam_key='other.exam')),
        ('mixed_version', lambda r: r['student_state'].update(profile_version='1.0')),
        ('self_correction', lambda r: r['assessment_event'].update(supersedes_event_id='fixture.event')),
        ('unresolved_event', lambda r: r['session_checkpoint']['event_refs'].append('unknown.event')),
        ('wrong_accuracy_ratio', lambda r: r['assessment_event']['metric'].update(kind='raw_accuracy', value=.7, numerator=8, denominator=10)),
        ('overfull_accuracy', lambda r: r['assessment_event']['metric'].update(kind='raw_accuracy', value=1.2, numerator=12, denominator=10)),
        ('origin_mismatch', lambda r: r['assessment_event'].update(material_type='OFFICIAL_PAST')),
        ('checkpoint_edition_mismatch', lambda r: r['session_checkpoint']['context'].update(edition_version='other')),
        ('checkpoint_stage_mismatch', lambda r: r['session_checkpoint']['context'].update(stage='other')),
        ('checkpoint_jurisdiction_mismatch', lambda r: r['session_checkpoint']['context'].update(jurisdiction='other')),
        ('orphan_correction', lambda r: r['assessment_event'].update(event_kind='CORRECTION', supersedes_event_id='missing.original')),
        ('orphan_profile_source', lambda r: r['exam_profile'].update(status='verified', source_ids=['missing.source'])),
        ('orphan_item_source', lambda r: r['item_record']['source_ids'].append('missing.source')),
        ('orphan_derived_event', lambda r: r['assessment_event']['derived_from_event_ids'].append('missing.event')),
        ('orphan_evidence_basis', lambda r: r['evidence_record']['basis_ids'].append('missing.evidence')),
    ]
    for label, mutate in bundle_negatives:
        bundle = deepcopy(records)
        mutate(bundle)
        try:
            validate_bundle(bundle)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError(f'Cross-record negative accepted: {label}')
    # A real predecessor is supplied and preserved when a correction is tested.
    corrected = deepcopy(records)
    corrected['event_history'] = [deepcopy(corrected['assessment_event'])]
    corrected['assessment_event'].update(event_id='fixture.correction', event_kind='CORRECTION', supersedes_event_id='fixture.event')
    corrected['student_state']['applied_event_ids'] = ['fixture.correction']
    corrected['session_checkpoint']['event_refs'] = ['fixture.correction']
    validate_bundle(corrected)
    checks += 1
    annulled = deepcopy(corrected)
    annulled['item_record'].update(annulled=True, eligibility='DISCARD')
    annulled['assessment_event'].update(eligible_for_mastery=False)
    validate_bundle(annulled)
    checks += 1
    counted_original = deepcopy(annulled)
    counted_original['student_state']['applied_event_ids'] = ['fixture.event']
    try:
        validate_bundle(counted_original)
    except AssertionError:
        checks += 1
    else:
        raise AssertionError('Historical annulled answer counted in current state')
    # A supplied external source resolves profile rules and an official report.
    verified = deepcopy(records)
    verified['evidence_record'].update(claim='Synthetic source for a contract test, not an actual examination report.', claim_class='EXTERNAL_FACT', origin='external', confidence='verified', source_ref='urn:fixture:source', retrieved_at='2026-10-05T00:00:00Z')
    verified['exam_profile'].update(status='verified', source_ids=['fixture.evidence'])
    verified['exam_profile']['scoring']['minimum_rules'] = [{'component':'A','minimum':60,'metric_kind':'scaled_score','unit':'scale 0–100','source_id':'fixture.evidence'}]
    verified['exam_profile']['scoring']['component_weights'] = [{'component':'A','weight':2,'unit':'scale 0–100','source_id':'fixture.evidence'}]
    validate_bundle(verified)
    checks += 1
    official = deepcopy(verified)
    official['assessment_event'].update(event_kind='OFFICIAL_RESULT', origin='external', item_ids=[], evidence_ids=['fixture.evidence'], material_type=None, assistance='NOT_APPLICABLE', previous_exposure='not_applicable', response_before_reveal=None, eligible_for_mastery=False)
    official['assessment_event']['metric'].update(kind='scaled_score', value=70, unit='scale 0–100', official=True)
    validate_bundle(official)
    checks += 1
    for label, mutation in [
        ('double_counted_correction', lambda r: r['student_state']['applied_event_ids'].append('fixture.event')),
        ('duplicate_event_id', lambda r: r['event_history'].append(deepcopy(r['event_history'][0]))),
        ('cyclic_event_history', lambda r: r['event_history'][0].update(event_kind='CORRECTION', supersedes_event_id='fixture.correction')),
    ]:
        candidate = deepcopy(corrected)
        mutation(candidate)
        try:
            validate_bundle(candidate)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError(f'History negative accepted: {label}')
    nested = skill / 'references/operations/context_policy.md'
    assert resolve_link(nested, '../knowledge/scoring.md', skill) == (skill / 'references/knowledge/scoring.md').resolve()
    try:
        resolve_link(nested, 'references/knowledge/scoring.md', skill)
    except AssertionError:
        checks += 2
    else:
        raise AssertionError('Skill-root link incorrectly accepted inside nested document')
    ids = []
    for file in (skill / 'references/evals/cases').glob('*.json'):
        suite = load(file)
        assert suite['fixture_notice']
        for case in suite['cases']:
            assert case['severity'] in ('P0', 'P1') and case['expected'] and case['forbidden']
            ids.append(case['id'])
            checks += 1
    assert len(ids) == len(set(ids)) == 62, 'Case inventory mismatch'
    checks += 1
    citations = dated_citations(skill)
    return {'status': 'PASS', 'documentary_checks': checks, 'schema_contracts': len(records),
            'valid_fixtures': len(records), 'valid_correction_histories': 1,
            'valid_annulment_histories': 1,
            'valid_verified_profile_sets': 1, 'valid_official_report_sets': 1,
            'negative_record_tests': len(negatives) + len(bundle_negatives) + 4,
            'academic_negative_tests': len(academic_negatives),
            'academic_review_fixtures_validated': 2,
            'dated_citations': len(citations),
            'oldest_citation_date': min((c[2] for c in citations), default=None),
            'behavioral_cases_defined': len(ids), 'behavioral_cases_executed_by_script': 0,
            'schema_validator_scope': 'explicit keywords used in this package only',
            'host_activation_tested': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    try:
        result = run(args.skill_root.resolve(), args.baseline.resolve() if args.baseline else None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (AssertionError, KeyError, ValueError, OSError) as error:
        print(json.dumps({'status': 'FAIL', 'reason': str(error)}, ensure_ascii=False))
        sys.exit(1)
