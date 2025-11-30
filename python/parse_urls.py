from message import (RunUrlMessage, get_all_env, get_user_name)
import json
import shutil
import sqlite3
import subprocess
import os
from windows_toasts import Toast, WindowsToaster
from windows_toasts.wrappers import ToastDuration

def _get_app_path(app_path, app_name):
    if os.path.exists(app_path):
        return app_path
    username = get_user_name()
    chrome_paths = [
        f'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        f'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    ]
    edge_paths = [
        f'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        f'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe'
    ]
    opera_paths = [
        f'C:\\Users\\{username}\\AppData\\Local\\Programs\\Opera\\opera.exe'
    ]

    if app_name == 'Chrome':
        for path in chrome_paths:
            if os.path.exists(path):
                return path
    elif app_name == 'Edge':
        for path in edge_paths:
            if os.path.exists(path):
                return path    
    elif app_name == 'Opera':
        for path in opera_paths:
            if os.path.exists(path):
                return path

    input(f'Cannot find {app_name} browser, update app path in user_configuration.json ...')
    return None

def _get_history_path(history_path, app_name):
    if os.path.exists(history_path):
        return history_path

    username = get_user_name()
    chrome_history_paths = [
        f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\History',
        f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History'
    ]
    edge_history_paths = [
        f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1\\History',
        f'C:\\Users\\{username}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History'
    ]
    opera_history_paths = [
        f'C:\\Users\\{username}\\AppData\\Roaming\\Opera Software\\Opera Stable\\Default\\History'
    ]

    if app_name == 'Chrome':
        for path in chrome_history_paths:
            if os.path.exists(path):
                return path
    elif app_name == 'Edge':
        for path in edge_history_paths:
            if os.path.exists(path):
                return path
    elif app_name == 'Opera':
        for path in opera_history_paths:
            if os.path.exists(path):
                return path

    input(f'Cannot find {app_name} browser history, update history path in user_configuration.json ...')
    return None

def main(message: RunUrlMessage, url_path: str, user_path: str):
    with open(url_path, 'r') as url_file:
        mapper = json.load(url_file)
    with open(user_path, 'r') as user_file:
        user_config = json.load(user_file)
    
    count = message.num
    operator = message.operator
    browser = _get_browser(user_config, message.env)
    browser_debug_port = browser['debug_port']
    browser_name = browser['app_name']
    browser_app_path = _get_app_path(browser['app_path'], browser_name)
    browser_history_path = _get_history_path(browser['history_path'], browser_name)
    browser_history_shadow_path = browser_history_path + '-Shadow'
    shutil.copy(browser_history_path, browser_history_shadow_path)
    switches = [message.switch_1, message.switch_2, message.switch_3]
    switches = [switch for switch in switches if switch]

    # Update mapper and switches
    if message.command in mapper:
        mapper = mapper[message.command]
        existing_switch = next((switch for switch in switches if switch in mapper), None)
        while existing_switch:
            mapper = mapper[existing_switch]
            switches.remove(existing_switch)
            existing_switch = next((switch for switch in switches if switch in mapper), None)
    else:
        switches.append(message.command)

    # Find the url
    url = ''
    url = find_link(browser_history_shadow_path, mapper[message.env][0], count, operator, switches)
    if url == '':
        url = mapper[message.env][1]
        for switch  in switches:
            url = url.replace('@', switch, 1)

    subprocess.Popen([browser_app_path, f'--remote-debugging-port={browser_debug_port}' , url])


def remove_common_parts(strings):
    if not strings:
        return []
    
    import re
    from urllib.parse import unquote, urlparse, parse_qs
    
    result = []
    for s in strings:
        try:
            parsed_url = urlparse(s)
            path = parsed_url.path
            fragment = parsed_url.fragment
            query = parsed_url.query
            
            extracted_info = None
            
            # --- SQS ---
            if "#/queues/" in s:
                try:
                    encoded = fragment.split("#/queues/")[1] if "#/queues/" in fragment else s.split("#/queues/")[1]
                    decoded = unquote(encoded)
                    parts = decoded.split("/")
                    known_subpages = ["send-receive", "dead-letter-queue", "monitoring", "permissions"]
                    name = parts[-1] if parts else ""
                    if name in known_subpages and len(parts) > 1:
                        name = parts[-2]
                    if name:
                        extracted_info = f"SQS: {name}"
                except:
                    pass
            
            # --- DynamoDB ---
            elif "/dynamodbv2/" in path and "table" in fragment:
                try:
                    name_match = re.search(r'name=([^&]+)', fragment)
                    if name_match:
                        table_name = unquote(name_match.group(1))
                        extracted_info = f"DDB: {table_name}"
                except:
                    pass
            
            # --- S3 ---
            elif "/s3/buckets/" in path or "s3/buckets/" in fragment or "prefix=" in query:
                try:
                    bucket_name = None
                    prefix = None
                    
                    # Extract from path
                    path_match = re.search(r'/s3/buckets/([^/?]+)', path)
                    if path_match:
                        bucket_name = path_match.group(1)
                    
                    # Extract from fragment
                    hash_match = re.search(r's3/buckets/([^/?]+)', fragment)
                    if hash_match:
                        bucket_name = hash_match.group(1)
                    
                    # Extract prefix
                    query_params = parse_qs(query)
                    if 'prefix' in query_params:
                        prefix = query_params['prefix'][0]
                    else:
                        prefix_match = re.search(r'prefix=([^&]+)', fragment)
                        if prefix_match:
                            prefix = unquote(prefix_match.group(1))
                    
                    if bucket_name:
                        if prefix:
                            extracted_info = f"S3: {bucket_name}/{prefix}"
                        else:
                            extracted_info = f"S3: {bucket_name}"
                except:
                    pass
            
            # --- CloudWatch Log Group ---
            elif "logsV2:log-groups/log-group/" in fragment:
                try:
                    lg_match = re.search(r'log-group/([^#]+)', fragment, re.IGNORECASE)
                    if lg_match:
                        encoded = lg_match.group(1)
                        decoded = unquote(encoded)
                        parts = [p for p in decoded.split("/") if p]
                        last_part = parts[-1] if parts else decoded
                        extracted_info = f"LG: {last_part}"
                except:
                    pass
            
            # --- CloudWatch Logs Insights ---
            elif "logs-insights" in fragment:
                try:
                    source_match = re.search(r'source~\(~\'([^)]+)\)', fragment, re.IGNORECASE)
                    if source_match:
                        encoded = source_match.group(1)
                        # Convert *XX hex encoding to %XX percent encoding
                        percent_encoded = re.sub(r'\*([0-9A-Fa-f]{2})', r'%\1', encoded)
                        decoded = unquote(percent_encoded)
                        last_part = decoded.split("/")[-1]
                        last_part = re.sub(r'[)\'"\s]+$', '', last_part)
                        extracted_info = f"CW: {last_part}"
                except:
                    pass
            
            # --- Lambda ---
            elif "/lambda/" in path and "#/functions" in fragment:
                try:
                    function_name = None
                    path_match = re.search(r'#/functions/([^?/]+)', fragment)
                    if path_match:
                        function_name = unquote(path_match.group(1))
                    else:
                        v0_match = re.search(r'v0=([^&]+)', fragment)
                        if v0_match:
                            function_name = unquote(v0_match.group(1))
                    
                    if function_name:
                        extracted_info = f"λ: {function_name}"
                except:
                    pass
            
            # --- ECS ---
            elif "/ecs/v2/clusters/" in path:
                try:
                    parts = [p for p in path.split("/") if p]
                    clusters_idx = parts.index("clusters") if "clusters" in parts else -1
                    
                    if clusters_idx >= 0 and len(parts) > clusters_idx + 1:
                        cluster_name = parts[clusters_idx + 1]
                        services_idx = parts.index("services") if "services" in parts else -1
                        
                        if services_idx >= 0 and len(parts) > services_idx + 1:
                            service_name = parts[services_idx + 1]
                            subpages = ["tasks", "health", "deployments", "metrics", "configuration", "logs", "events"]
                            
                            if service_name not in subpages:
                                extracted_info = f"ECS: {service_name}"
                            else:
                                extracted_info = f"ECS: {cluster_name}"
                        else:
                            extracted_info = f"ECS: {cluster_name}"
                except:
                    pass
            
            # --- EC2 Instance ---
            elif "InstanceDetails:instanceId=" in fragment or "InstanceDetails:" in fragment:
                try:
                    id_match = re.search(r'instanceId=([^&]+)', fragment, re.IGNORECASE)
                    instance_id = None
                    if id_match:
                        instance_id = unquote(id_match.group(1))
                    else:
                        alt_match = re.search(r'InstanceDetails:([^&?/]+)', fragment, re.IGNORECASE)
                        if alt_match:
                            instance_id = unquote(alt_match.group(1))
                    
                    if instance_id:
                        extracted_info = f"EC2: {instance_id}"
                except:
                    pass
            
            # --- Load Balancer ---
            elif "LoadBalancer:loadBalancerArn=" in fragment or "LoadBalancer:" in fragment:
                try:
                    arn_match = re.search(r'loadBalancerArn=([^&;]+)', fragment, re.IGNORECASE) or re.search(r'LoadBalancer:([^&;]+)', fragment, re.IGNORECASE)
                    if arn_match:
                        decoded = unquote(arn_match.group(1))
                        lb_match = re.search(r'loadbalancer/(?:app|net)/([^/;]+)', decoded, re.IGNORECASE)
                        if lb_match:
                            lb_name = lb_match.group(1)
                            extracted_info = f"LB: {lb_name}"
                except:
                    pass
            
            # --- Security Group ---
            elif "SecurityGroup:" in fragment or "groupId=sg-" in fragment:
                try:
                    gid_match = re.search(r'groupId=(sg-[0-9a-fA-F-]+)', fragment, re.IGNORECASE) or re.search(r'SecurityGroup:([^&;]+)', fragment, re.IGNORECASE)
                    if gid_match:
                        sg_id = unquote(gid_match.group(1))
                        extracted_info = f"SG: {sg_id}"
                except:
                    pass
            
            # --- CloudFormation ---
            elif "#/stacks/stackinfo" in fragment or "/stacks/stackinfo" in fragment:
                try:
                    stack_id_match = re.search(r'stackId=([^&]+)', fragment, re.IGNORECASE)
                    if stack_id_match:
                        decoded = unquote(stack_id_match.group(1))
                        parts = [p for p in decoded.split('/') if p]
                        stack_idx = next((i for i, p in enumerate(parts) if p.lower() == 'stack'), -1)
                        if stack_idx >= 0 and len(parts) > stack_idx + 1:
                            stack_name = parts[stack_idx + 1]
                            extracted_info = f"CF: {stack_name}"
                except:
                    pass
            
            # --- Secrets Manager ---
            elif "/secretsmanager/secret" in path:
                try:
                    query_params = parse_qs(query)
                    if 'name' in query_params:
                        decoded = unquote(query_params['name'][0])
                        extracted_info = f"🔑 {decoded}"
                except:
                    pass
            
            # If we extracted meaningful info, use it; otherwise fallback to original logic
            if extracted_info:
                result.append(extracted_info)
            else:
                # Fallback: extract meaningful part after removing common prefix
                common_prefix = os.path.commonprefix(strings)
                remaining = s[len(common_prefix):]
                # Extract last meaningful segment
                segments = remaining.split('%2F')
                if segments:
                    last_segment = segments[-1].split('/')[0]  # Remove /send-receive if present
                    result.append(last_segment)
                else:
                    result.append(remaining)
        
        except Exception:
            # On any error, use the original URL as fallback
            result.append(s)
    
    return result

def move_index_to_start(lst, number):
    index = number - 1  # Calculate the desired index (number - 1)
    if 0 <= index < len(lst):  # Check if the index is valid
        # Remove the item at the index and insert it at the start
        item = lst.pop(index)
        lst.insert(0, item)
    return lst

def find_link(browser_history_shadow_path, base_url, count=1, operator='and', terms=[]):
    with sqlite3.connect(browser_history_shadow_path) as con:
        cursor = con.cursor()
        if '@' not in base_url:
            return base_url
        terms = [base_url.replace('@', f'%{term}%') for term in terms] if terms else [base_url.replace('@', '%')]
        placeholders = f' {operator} '.join('url LIKE ?' for term in terms)
        query = f"""
            SELECT DISTINCT url 
            FROM urls 
            WHERE {placeholders}
            ORDER BY last_visit_time DESC"""
        cursor.execute(query, (terms))
        urls = cursor.fetchall()
        output = remove_common_parts([x[0] for x in urls])
        output = move_index_to_start(output, int(count))
        shorten_output = [x[:50] for x in output]
        # Add 1-based index to each record and remove duplicates while preserving original indices
        indexed_output = []
        seen_content = set()

        for i, content in enumerate(shorten_output, 1):
            if content not in seen_content:
                indexed_output.append(f"{i} {content}")
                seen_content.add(content)
        
        toaster = WindowsToaster(f'{len(urls)} URLs')
        toaster.clear_toasts()
        newToast = Toast(['\n'.join([x[:40] for x in indexed_output])], duration=ToastDuration.Long)
        toaster.show_toast(newToast)
        return '' if not urls else urls[int(count)-1][0]

def _get_browser(config, env):
    all_env = get_all_env()
    env_index = all_env.index(env)
    browser_list = config.get('browsers', [])
    for key, value in browser_list.items():
        if value['env_id'] == env_index:
            return value
    print("Cannot read valid env to set the browser")
    input()
    exit()

def convert_nested_dict(d):
    return {key: convert_nested_dict(value) if isinstance(value, dict) else value for key, value in d.items()}