#!/usr/bin/env python3
"""
Custom test runner for the Sauce Playwright POM project.
"""
import click
import subprocess
import uuid
from pathlib import Path
import shutil
import json
import xml.etree.ElementTree as ET
import platform
import time
import os
import html as _html

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"
VIDEOS = ROOT / "videos"
SCREENSHOTS = ROOT / "screenshots"
SESSION_DIR = ROOT / "session"

def ensure_dirs():
    for d in (REPORTS, LOGS, VIDEOS, SCREENSHOTS, SESSION_DIR):
        d.mkdir(parents=True, exist_ok=True)

def clear_previous():
    for d in (REPORTS, LOGS, VIDEOS, SCREENSHOTS):
        if d.exists():
            for child in d.iterdir():
                try:
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                    elif child.is_dir():
                        shutil.rmtree(child)
                except Exception:
                    pass

def discover_tests(path: Path, pattern: str = "test_*.py"):
    return [p for p in path.rglob(pattern) if p.is_file()]

def run_pytest(test_args, html_path: Path, junit_path: Path, parallel: int = 0):
    cmd = ["pytest"] + test_args + [f"--html={html_path}", f"--self-contained-html", f"--junitxml={junit_path}"]
    if parallel and parallel > 0:
        cmd = ["pytest", f"-n", str(parallel)] + test_args + [f"--html={html_path}", f"--self-contained-html", f"--junitxml={junit_path}"]
    print("Running:", " ".join(cmd))
    start = time.time()
    res = subprocess.run(cmd)
    duration = time.time() - start
    return res.returncode, duration

def parse_junit(junit_file: Path):
    if not junit_file.exists():
        return {"passed": 0, "failed": 0, "skipped": 0, "tests": [], "duration": 0.0}
    tree = ET.parse(str(junit_file))
    root = tree.getroot()
    passed = failed = skipped = 0
    tests = []
    total_time = 0.0
    for testcase in root.iter('testcase'):
        t = {
            'classname': testcase.attrib.get('classname'),
            'name': testcase.attrib.get('name'),
            'time': float(testcase.attrib.get('time', '0')),
            'file': None,
            'status': 'passed'
        }
        total_time += t['time']
        if testcase.find('failure') is not None or testcase.find('error') is not None:
            t['status'] = 'failed'
            failed += 1
        elif testcase.find('skipped') is not None:
            t['status'] = 'skipped'
            skipped += 1
        else:
            passed += 1
        tests.append(t)
    return {"passed": passed, "failed": failed, "skipped": skipped, "tests": tests, "duration": total_time}

def failed_nodeids_from_junit(junit_file: Path):
    parsed = parse_junit(junit_file)
    nodeids = []
    for t in parsed['tests']:
        if t['status'] == 'failed':
            cls = t.get('classname')
            name = t.get('name')
            candidate_paths = []
            if cls:
                candidate_paths.append(Path(cls.replace('.', '/') + '.py'))
            if cls and '.' in cls:
                candidate_paths.append(Path(cls.split('.')[-1] + '.py'))
            for p in (REPORTS.parent).rglob('**/*.py'):
                try:
                    text = p.read_text(encoding='utf-8')
                except Exception:
                    continue
                if f'def {name}(' in text or name in text:
                    candidate_paths.append(p.relative_to(REPORTS.parent))
            picked = None
            for c in candidate_paths:
                c_path = (REPORTS.parent / c) if not c.is_absolute() else c
                if c_path.exists():
                    picked = c_path
                    break
            if picked is None:
                if cls:
                    picked = REPORTS.parent / (cls.replace('.', '/') + '.py')
                else:
                    continue
            nodeids.append(f"{picked}::{name}")
    return nodeids

def collect_videos_map(videos_root: Path):
    mapping = {}
    if not videos_root.exists():
        return mapping
    for folder in videos_root.iterdir():
        if not folder.is_dir():
            continue
        meta_f = folder / 'metadata.json'
        target_folder = folder
        if not meta_f.exists():
            for sub in folder.iterdir():
                if sub.is_dir():
                    m = sub / 'metadata.json'
                    if m.exists():
                        meta_f = m
                        target_folder = sub
                        break
        try:
            data = json.loads(meta_f.read_text()) if meta_f.exists() else None
        except Exception:
            data = None
        nodeid = data.get('nodeid') if data else None
        if nodeid:
            vids = [str(p) for p in target_folder.rglob('*') if p.is_file() and p.name != 'metadata.json']
            mapping[nodeid] = vids
            try:
                if nodeid.startswith(str(ROOT)):
                    rel = nodeid[len(str(ROOT)) + 1:]
                    mapping.setdefault(rel, vids)
            except Exception:
                pass
            try:
                abs_node = str((REPORTS.parent / nodeid))
                mapping.setdefault(abs_node, vids)
            except Exception:
                pass
    return mapping

# --- UPDATED INJECTION LOGIC ---
def inject_videos_into_pytest_html(html_path: Path, videos_map: dict, failed_nodeids: list):
    if not html_path.exists():
        return

    print("Injecting videos into report...")
    text = html_path.read_text(encoding='utf-8')
    
    prefix = 'data-jsonblob="'
    start_idx = text.find(prefix)
    if start_idx == -1: return
    
    start_content = start_idx + len(prefix)
    end_idx = text.find('">', start_content)
    if end_idx == -1: return

    blob_raw = text[start_content:end_idx]
    try:
        blob_json = _html.unescape(blob_raw)
        data = json.loads(blob_json)
    except Exception as e:
        print(f"Error parsing report JSON: {e}")
        return

    injected_count = 0
    
    def find_videos(test_key):
        if test_key in videos_map: return videos_map[test_key]
        suffix = test_key.split('/')[-1]
        for k, v in videos_map.items():
            if k.endswith(suffix):
                return v
        return []

    tests_dict = data.get('tests', {})
    
    for test_key, results_list in tests_dict.items():
        target_result = None
        for res in results_list:
            if res.get('result', '').lower() == 'failed':
                target_result = res
                break
        
        if not target_result: continue 

        vids = find_videos(test_key)
        if not vids: continue

        rel_paths = []
        for v_path in vids:
            try:
                rel = os.path.relpath(v_path, REPORTS)
                rel_paths.append(rel)
            except ValueError:
                rel_paths.append(v_path)

        # 1. Inject "Badge" Link into Table
        if 'resultsTableRow' in target_result:
            row_html = target_result['resultsTableRow']
            link_idx = -1
            for i, cell in enumerate(row_html):
                if 'col-links' in cell:
                    link_idx = i
                    break
            
            if link_idx != -1:
                links_html = ""
                for i, r_path in enumerate(rel_paths):
                    label = "Video" if len(rel_paths) == 1 else f"Video {i+1}"
                    # Badge Style: Red background, white text, rounded corners
                    style = (
                        "background-color: #d9534f; color: white; padding: 2px 6px; "
                        "border-radius: 4px; text-decoration: none; font-size: 11px; "
                        "margin-right: 4px; display: inline-block;"
                    )
                    links_html += f'<a href="{r_path}" target="_blank" style="{style}">{label}</a>'
                
                old_cell = row_html[link_idx]
                if '</td>' in old_cell:
                    new_cell = old_cell.replace('</td>', f'{links_html}</td>')
                    row_html[link_idx] = new_cell

        # 2. Inject Compact Player
        video_html_list = []
        for r_path in rel_paths:
            html = (
                f'<div class="media" style="float: left; margin: 10px 0; clear: both;">'
                f'<div style="margin-bottom: 4px; font-weight: bold; font-size: 12px; color: #555;">Video Evidence:</div>'
                # UPDATED: Fixed width 480px for better fit
                f'<video controls style="width: 480px; max-width: 100%; border: 1px solid #ccc; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); background: #000;">'
                f'<source src="{r_path}" type="video/webm">'
                f'Your browser does not support the video tag.'
                f'</video>'
                f'</div>'
            )
            video_html_list.append(html)

        target_result.setdefault('tableHtml', [])
        target_result['tableHtml'].extend(video_html_list)
        injected_count += 1

    if injected_count > 0:
        new_json_str = json.dumps(data)
        new_blob = _html.escape(new_json_str, quote=True)
        new_text = text[:start_content] + new_blob + text[end_idx:]
        html_path.write_text(new_text, encoding='utf-8')
        print(f"Successfully injected videos for {injected_count} failed tests.")

def make_pie_chart(stats, outpath: Path, title: str = "Test Results"):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib not installed; skipping pie chart generation')
        return
    labels = ['passed', 'failed', 'skipped']
    sizes = [stats.get('passed', 0), stats.get('failed', 0), stats.get('skipped', 0)]
    colors = ['#2ecc71', '#e74c3c', '#f1c40f']
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title(title)
    plt.savefig(outpath)
    plt.close()

@click.command()
@click.option('--path', '-p', default='.', help='Path to tests (file or folder)')
@click.option('--pattern', default='test_*.py', help='Filename pattern for discovery')
@click.option('--parallel', '-n', default=0, type=int, help='Number of parallel workers (pytest-xdist)')
@click.option('--retries', '-r', default=0, type=int, help='Number of retries for failed tests')
@click.option('--clear/--no-clear', default=True, help='Clear previous reports, logs, videos and screenshots')
@click.option('--resume', is_flag=True, default=False, help='Resume from last session (retry failed tests)')
@click.option('--markers', default=None, help='Pytest markers to pass as -m')
@click.option('--kexpr', default=None, help='Pytest -k expression')
def main(path, pattern, parallel, retries, clear, resume, markers, kexpr):
    ensure_dirs()
    if clear:
        clear_previous()

    run_id = uuid.uuid4().hex[:8]
    session_file = SESSION_DIR / f'session_{run_id}.json'

    base_path = Path(path)
    if resume:
        last = sorted(SESSION_DIR.glob('session_*.json'))
        if not last:
            print('No previous session found to resume')
            return
        session_file = last[-1]
        with open(session_file) as fh:
            state = json.load(fh)
        nodeids = state.get('failed_nodeids', [])
        if not nodeids:
            print('No failed tests in last session')
            return
        print(f'Rerunning {len(nodeids)} failed tests from {session_file}')
        html = REPORTS / f'rerun_{session_file.stem}.html'
        junit = REPORTS / f'rerun_{session_file.stem}.xml'
        rc, duration = run_pytest(nodeids, html, junit, parallel)
        stats = parse_junit(junit)
        make_pie_chart(stats, REPORTS / f'chart_{run_id}.png', title=f'Retry {session_file.stem}')
        print('Rerun complete. See reports.')
        return

    if base_path.is_file():
        test_paths = [base_path]
    else:
        test_paths = discover_tests(base_path, pattern)

    if not test_paths:
        print('No tests found')
        return

    test_args = [str(p) for p in test_paths]
    if markers:
        test_args += ["-m", markers]
    if kexpr:
        test_args += ["-k", kexpr]

    html = REPORTS / f'report_{run_id}.html'
    junit = REPORTS / f'report_{run_id}.xml'
    rc, duration = run_pytest(test_args, html, junit, parallel)
    stats = parse_junit(junit)

    failed_nodeids = failed_nodeids_from_junit(junit)

    session_state = {
        'run_id': run_id,
        'stats': stats,
        'failed_nodeids': failed_nodeids,
        'duration': duration,
        'env': {
            'platform': platform.platform(),
            'python': platform.python_version()
        }
    }
    with open(session_file, 'w') as fh:
        json.dump(session_state, fh, indent=2)

    attempt = 0
    while retries > 0 and failed_nodeids:
        attempt += 1
        print(f'Retry attempt {attempt} for {len(failed_nodeids)} tests')
        html_r = REPORTS / f'retry_{run_id}_{attempt}.html'
        junit_r = REPORTS / f'retry_{run_id}_{attempt}.xml'
        rc2, dur2 = run_pytest(failed_nodeids, html_r, junit_r, parallel)
        parsed2 = parse_junit(junit_r)
        failed_nodeids = []
        for t in parsed2['tests']:
            if t['status'] == 'failed':
                cls = t.get('classname')
                name = t.get('name')
                if cls:
                    path = cls.replace('.', '/') + '.py'
                    failed_nodeids.append(f"{path}::{name}")
        retries -= 1
        session_state['failed_nodeids'] = failed_nodeids
        session_state['stats_retry_' + str(attempt)] = parsed2
        with open(session_file, 'w') as fh:
            json.dump(session_state, fh, indent=2)

    make_pie_chart(stats, REPORTS / f'chart_{run_id}.png', title=f'Run {run_id}')

    try:
        videos_map = collect_videos_map(VIDEOS)
        inject_videos_into_pytest_html(html, videos_map, failed_nodeids)
    except Exception as e:
        print('Failed to inject videos into pytest-html report:', e)

    print('Run complete')
    print(f'Reports: {html}')
    print(f'Junit: {junit}')
    print(f'Chart: {REPORTS / f"chart_{run_id}.png"}')

if __name__ == '__main__':
    main()