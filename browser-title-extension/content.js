(function () {
    console.info("AWS Tab Title Renamer Loaded");

    let lastTitle = document.title;
    let titleUpdateTimer;
    const safeSetTitle = (newTitle) => {
        if (newTitle && newTitle !== document.title) {
            lastTitle = newTitle;
            document.title = newTitle;
        }
    };

    // Helper function for resource name (bold formatting is handled by tab-navigator.js)
    const formatResourceName = (name) => name;

    // Rewrite visible "ChatGPT" text to "Reports", skipping editable/script content
    const replaceBrandingInPageText = () => {
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
            acceptNode: (node) => {
                if (!node.nodeValue || !node.nodeValue.includes('ChatGPT')) return NodeFilter.FILTER_REJECT;
                const parent = node.parentElement;
                if (!parent || parent.closest('script, style, textarea, input, [contenteditable="true"]')) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        });
        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        nodes.forEach(node => {
            node.nodeValue = node.nodeValue.replace(/ChatGPT/g, 'Reports');
        });
    };

    const updateFavicon = (emoji) => {
        if (!emoji) return;
        
        // Remove existing favicons
        const existingLinks = document.querySelectorAll("link[rel*='icon']");
        existingLinks.forEach(link => link.remove());
        
        // Create canvas to render emoji as favicon
        const canvas = document.createElement('canvas');
        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');
        
        // Draw emoji
        ctx.font = '48px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(emoji, 32, 32);
        
        // Create new favicon link
        const link = document.createElement('link');
        link.rel = 'icon';
        link.href = canvas.toDataURL('image/png');
        document.head.appendChild(link);
    };

    const removeFavicon = () => {
        document.querySelectorAll("link[rel*='icon']").forEach(link => link.remove());
        const transparentIcon = document.createElement('link');
        transparentIcon.rel = 'icon';
        transparentIcon.href = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=';
        document.head.appendChild(transparentIcon);
    };

    const updateTitle = () => {
        const url = new URL(location.href);
        const hash = url.hash || "";
        let newTitle = null;
        let favicon = null;

        // Use AWS icon for AWS sign-in/authorization pages
        const isAwsSignInPage = url.hostname.includes('signin.aws.amazon.com') || 
                                url.pathname.includes('/oauth') ||
                                url.search.includes('oauth-flow-id');
        
        if (isAwsSignInPage) {
            // Use AWS icon for sign-in pages
            const awsIconUrl = chrome.runtime.getURL('icons/aws/aws.ico');
            const existingLinks = document.querySelectorAll("link[rel*='icon']");
            existingLinks.forEach(link => link.remove());
            
            const link = document.createElement('link');
            link.rel = 'icon';
            link.href = awsIconUrl;
            document.head.appendChild(link);
            return;
        }

        // --- SQS ---
        if (hash.includes("#/queues")) {
            try {
                // Check if we're on the main queues list page (no specific queue)
                if (hash === "#/queues" || hash.startsWith("#/queues?")) {
                    newTitle = "[SQS]";
                } else if (hash.includes("#/queues/")) {
                    // Specific queue selected
                    const encoded = hash.split("#/queues/")[1];
                    const decoded = decodeURIComponent(encoded);
                    const parts = decoded.split("/");
                    const knownSubpages = ["send-receive", "dead-letter-queue", "monitoring", "permissions"];
                    let name = parts.pop();
                    if (knownSubpages.includes(name) && parts.length > 0) name = parts.pop();
                    newTitle = `[SQS] ${formatResourceName(name)}`;
                }
            } catch (e) {
                console.error("SQS parsing error:", e);
            }
        }

        // --- DynamoDB ---
        if (url.pathname.includes("/dynamodbv2/")) {
            try {
                // Check if we're on the main dashboard page (no specific table)
                if (hash === "#dashboard" || hash === "" || !hash.includes("table")) {
                    newTitle = "[DynamoDB]";
                } else if (hash.includes("edit-item") && hash.includes("table=") && hash.includes("pk=")) {
                    // Item editor/viewer page with table and primary key
                    const tableMatch = hash.match(/table=([^&]+)/);
                    const pkMatch = hash.match(/pk=([^&]+)/);
                    
                    if (tableMatch && pkMatch) {
                        const tableName = decodeURIComponent(tableMatch[1]);
                        const pkValue = decodeURIComponent(pkMatch[1]);
                        
                        // Shorten the pk if it's very long (keep first part)
                        let pkDisplay = pkValue;
                        if (pkValue.length > 40) {
                            // Take first part before # or first 20 chars
                            const firstPart = pkValue.split('#')[0];
                            pkDisplay = firstPart.length > 20 ? firstPart.substring(0, 20) + '...' : firstPart;
                        }
                        
                        newTitle = `${tableName} [${pkDisplay}] [DynamoDB]`;
                    }
                } else if (hash.includes("table")) {
                    // Match name= or table= parameter in hash
                    const nameMatch = hash.match(/(?:name|table)=([^&]+)/);
                    if (nameMatch) {
                        const tableName = decodeURIComponent(nameMatch[1]);
                        newTitle = `${formatResourceName(tableName)} [DynamoDB]`;
                    }
                }
            } catch (e) {
                console.error("DynamoDB parsing error:", e);
            }
        }

        // --- S3 ---
        if (url.pathname.includes("/s3/buckets/") || hash.includes("s3/buckets/") || url.search.includes("prefix=")) {
            try {
                let bucketName = null;
                let prefix = null;

                // Try to extract from pathname first
                const pathMatch = url.pathname.match(/\/s3\/buckets\/([^/?]+)/);
                if (pathMatch) {
                    bucketName = pathMatch[1];
                }

                // Try to extract from hash
                const hashMatch = hash.match(/s3\/buckets\/([^/?]+)/);
                if (hashMatch) {
                    bucketName = hashMatch[1];
                }

                // Extract prefix/path if present (from search params or hash)
                const searchParams = new URLSearchParams(url.search);
                if (searchParams.has("prefix")) {
                    prefix = searchParams.get("prefix");
                } else {
                    const prefixMatch = hash.match(/prefix=([^&]+)/);
                    if (prefixMatch) {
                        try {
                            prefix = decodeURIComponent(prefixMatch[1]);
                        } catch (e) {
                            prefix = prefixMatch[1];
                        }
                    }
                }

                if (bucketName) {
                    if (prefix) {
                        // Show full path
                        newTitle = `[S3] ${formatResourceName(bucketName + '/' + prefix)}`;
                    } else {
                        newTitle = `[S3] ${formatResourceName(bucketName)}`;
                    }
                }
            } catch (e) {
                console.error("S3 parsing error:", e);
            }
        }

        // --- CloudWatch Log Group ---
        // Matches URLs like: #logsV2:log-groups/log-group/%2Faws%2Flambda%2FDev-ME-Estimation-WorkerLambda
        if (hash.includes("logsV2:log-groups/log-group/")) {
            try {
                // capture the encoded log-group path after `log-group/`
                const lgMatch = hash.match(/log-group\/([^#]+)/i);
                if (lgMatch && lgMatch[1]) {
                    let encoded = lgMatch[1];
                    // decode percent-encoding
                    let decoded = decodeURIComponent(encoded);
                    // decoded may be like "/aws/lambda/Dev-ME-Estimation-WorkerLambda"
                    const parts = decoded.split("/").filter(p => p);
                    const lastPart = parts.length ? parts[parts.length - 1] : decoded;
                    newTitle = `[Log Group] ${formatResourceName(lastPart)}`;
                }
            } catch (e) {
                console.error("CloudWatch Log Group parsing error:", e);
            }
        }

        // --- CloudWatch Logs Insights ---
        if (hash.includes("logs-insights")) {
            try {
                // Match source parameter: source~(~'value) or source~(~'*2fvalue)
                const sourceMatch = hash.match(/source~\(~'([^)]+)\)/i);
                if (sourceMatch) {
                    let encoded = sourceMatch[1];
                    // Convert *XX hex encoding to %XX percent encoding
                    const percentEncoded = encoded.replace(/\*([0-9A-Fa-f]{2})/g, "%$1");
                    let decoded = decodeURIComponent(percentEncoded);
                    
                    // Extract last part after final slash
                    let lastPart = decoded.split("/").pop();
                    // Clean up any trailing characters
                    lastPart = lastPart.replace(/[)'"\s]+$/g, "");
                    newTitle = `[CW Insights] ${formatResourceName(lastPart)}`;
                }
            } catch (e) {
                console.error("Failed to parse CloudWatch log group name:", e);
            }
        }

        // --- CloudWatch Metrics ---
        // Matches URLs like: #metricsV2?graph=~(metrics~(~(~'AWS*2fElastiCache~...~'CacheClusterId~'prod-ina-forwarder-redis...
        if (hash.includes("#metricsV2") || hash.includes("metricsV2")) {
            try {
                // Try to extract resource identifiers from various AWS services
                // Look for common resource ID patterns in the metrics data
                const patterns = [
                    { name: 'CacheClusterId', regex: /CacheClusterId~'([^~']+)/ },
                    { name: 'LoadBalancerName', regex: /LoadBalancerName~'([^~']+)/ },
                    { name: 'DBInstanceIdentifier', regex: /DBInstanceIdentifier~'([^~']+)/ },
                    { name: 'FunctionName', regex: /FunctionName~'([^~']+)/ },
                    { name: 'InstanceId', regex: /InstanceId~'([^~']+)/ },
                    { name: 'QueueName', regex: /QueueName~'([^~']+)/ },
                    { name: 'TableName', regex: /TableName~'([^~']+)/ },
                ];

                let resourceName = null;
                for (const pattern of patterns) {
                    const match = hash.match(pattern.regex);
                    if (match && match[1]) {
                        resourceName = match[1];
                        break;
                    }
                }

                if (resourceName) {
                    newTitle = `[Metrics] ${formatResourceName(resourceName)}`;
                }
            } catch (e) {
                console.error("CloudWatch Metrics parsing error:", e);
            }
        }

        // --- Lambda ---
        // Handle both path-style hashes like `#/functions/FunctionName` and v0 param style
        if (url.pathname.includes("/lambda/") && hash.includes("#/functions")) {
            try {
                // Check if we're on the main functions list page (no specific function)
                if (hash === "#/functions" || hash.startsWith("#/functions?")) {
                    newTitle = "[Lambda]";
                } else {
                    // Try path-style: #/functions/FunctionName?tab=...
                    let functionName = null;
                    const pathMatch = hash.match(/#\/functions\/([^?\/]+)/);
                    if (pathMatch && pathMatch[1]) {
                        functionName = decodeURIComponent(pathMatch[1]);
                    } else {
                        // Fallback: check v0 parameter
                        const v0Match = hash.match(/v0=([^&]+)/);
                        if (v0Match && v0Match[1]) {
                            functionName = decodeURIComponent(v0Match[1]);
                        }
                    }

                    if (functionName) {
                        newTitle = `[Lambda] ${formatResourceName(functionName)}`;
                    }
                }
            } catch (e) {
                console.error("Lambda parsing error:", e);
            }
        }

        // --- ECS ---
        if (url.pathname.includes("/ecs/v2/clusters/")) {
            try {
                const parts = url.pathname.split("/").filter(p => p); // Remove empty parts
                const clustersIdx = parts.indexOf("clusters");
                
                if (clustersIdx >= 0 && parts.length > clustersIdx + 1) {
                    const clusterName = parts[clustersIdx + 1];
                    const servicesIdx = parts.indexOf("services");
                    
                    // Always show cluster name first since it's most important context
                    if (servicesIdx >= 0 && parts.length > servicesIdx + 1) {
                        // We have something after "services"
                        let serviceName = parts[servicesIdx + 1];
                        const subpages = ["tasks", "health", "deployments", "metrics", "configuration", "logs", "events"];
                        
                        // If serviceName is NOT a subpage, show both cluster and service
                        if (!subpages.includes(serviceName)) {
                            newTitle = `[ECS] ${formatResourceName(clusterName)} / ${formatResourceName(serviceName)}`;
                        } else {
                            // It's a subpage, show just cluster name
                            newTitle = `[ECS] ${formatResourceName(clusterName)}`;
                        }
                    } else {
                        // No service in path (just /clusters/name/services or /clusters/name), show cluster
                        newTitle = `[ECS] ${formatResourceName(clusterName)}`;
                    }
                }
            } catch (e) {
                console.error("ECS parsing error:", e);
            }
        }

        // --- EC2 Instance ---
        // Matches URLs like: #InstanceDetails:instanceId=i-03caea7934b5fe4d7
        if (hash.includes("InstanceDetails:instanceId=") || hash.includes("InstanceDetails:")) {
            try {
                const idMatch = hash.match(/instanceId=([^&]+)/i);
                let instanceId = null;
                if (idMatch && idMatch[1]) {
                    instanceId = decodeURIComponent(idMatch[1]);
                } else {
                    // fallback: sometimes the id is directly after InstanceDetails:
                    const altMatch = hash.match(/InstanceDetails:([^&?/]+)/i);
                    if (altMatch && altMatch[1]) instanceId = decodeURIComponent(altMatch[1]);
                }

                if (instanceId) {
                    newTitle = `[EC2] ${formatResourceName(instanceId)}`;
                }
            } catch (e) {
                console.error("EC2 parsing error:", e);
            }
        }

        // --- Load Balancer ---
        // Matches URLs like: #LoadBalancer:loadBalancerArn=arn:aws:elasticloadbalancing:region:acct:loadbalancer/app/Name/ID
        if (hash.includes("LoadBalancer:loadBalancerArn=") || hash.includes("LoadBalancer:loadBalancerArn") || hash.includes("LoadBalancer:")) {
            try {
                // Try to capture loadBalancerArn parameter
                const arnMatch = hash.match(/loadBalancerArn=([^&;]+)/i) || hash.match(/LoadBalancer:([^&;]+)/i);
                let lbName = null;
                if (arnMatch && arnMatch[1]) {
                    const decoded = decodeURIComponent(arnMatch[1]);
                    // Try a direct regex for app/net style: .../loadbalancer/(app|net)/<name>/id
                    const m = decoded.match(/loadbalancer\/(?:app|net)\/([^\/;]+)/i);
                    if (m && m[1]) {
                        lbName = m[1];
                    } else {
                        // decoded example: arn:aws:elasticloadbalancing:eu-west-1:acct:loadbalancer/app/Name/ID
                        // fallback: split on '/loadbalancer/' then pick second element's second segment
                        const markerSplit = decoded.split('/loadbalancer/');
                        if (markerSplit.length > 1) {
                            const after = markerSplit[1];
                            const parts = after.split('/').filter(p => p);
                            if (parts.length >= 2) {
                                lbName = parts[1];
                            } else if (parts.length === 1) {
                                lbName = parts[0];
                            }
                        } else {
                            // final fallback: try to find 'loadbalancer' segment and take name after type
                            const parts = decoded.split('/').filter(p => p);
                            const lbIdx = parts.findIndex(p => p.toLowerCase() === 'loadbalancer');
                            if (lbIdx >= 0 && parts.length > lbIdx + 2) {
                                lbName = parts[lbIdx + 2];
                            }
                        }
                    }
                }

                if (lbName) {
                    newTitle = `[LB] ${formatResourceName(lbName)}`;
                }
            } catch (e) {
                console.error('Load Balancer parsing error:', e);
            }
        }

        // --- Security Group ---
        // Matches URLs like: #SecurityGroup:groupId=sg-04ef1b81589011165
        if (hash.includes("SecurityGroup:") || hash.includes("groupId=sg-")) {
            try {
                // Try to capture groupId parameter
                const gidMatch = hash.match(/groupId=(sg-[0-9a-fA-F-]+)/i) || hash.match(/SecurityGroup:([^&;]+)/i);
                let sgId = null;
                if (gidMatch && gidMatch[1]) {
                    // If the match contains 'groupId=...' it will capture the id directly; otherwise decode
                    sgId = decodeURIComponent(gidMatch[1]);
                }

                if (sgId) {
                    newTitle = `[SG] ${formatResourceName(sgId)}`;
                }
            } catch (e) {
                console.error('Security Group parsing error:', e);
            }
        }

        // --- CloudFormation stack view ---
        // Matches URLs like:
        // #/stacks/stackinfo?filteringText=ina&stackId=arn%3Aaws%3Acloudformation%3A...%2FDev-InA-Manual-Bulk-Sender%2F...
        // Also matches list view: #/stacks?filteringStatus=active&filteringText=&viewNested=true
        if (url.pathname.includes("/cloudformation/") || hash.includes("/stacks")) {
            try {
                let stackName = null;

                // Check for list view (stacks page without specific stack)
                if (hash === "#/stacks" || (hash.startsWith("#/stacks?") && !hash.includes("stackinfo") && !hash.includes("stackId="))) {
                    newTitle = "[CF]";
                }
                // Check for stackinfo view (detail page)
                else if (hash.includes("stackinfo") || hash.includes("stackId=")) {
                    // Extract stackId parameter from hash or search
                    // Look for stackId=... in the hash
                    const stackIdMatch = hash.match(/stackId=([^&]+)/i);
                    if (stackIdMatch && stackIdMatch[1]) {
                        // Decode percent-encoding
                        const decoded = decodeURIComponent(stackIdMatch[1]);
                        // ARN contains .../StackName/UUID - split on '/' and take the element before the UUID
                        const parts = decoded.split('/').filter(p => p);
                        // ARN format: arn:aws:cloudformation:region:acct:stack/StackName/UUID
                        // find "stack" segment and take next part as stack name if present
                        const stackIdx = parts.findIndex(p => p.toLowerCase() === 'stack');
                        if (stackIdx >= 0 && parts.length > stackIdx + 1) {
                            stackName = parts[stackIdx + 1];
                        } else {
                            // fallback: take last non-empty segment (before UUID)
                            stackName = parts.length > 1 ? parts[parts.length - 2] : (parts.length ? parts[parts.length - 1] : null);
                        }
                    }

                    // If not found in hash, check search params in the URL
                    if (!stackName) {
                        const searchParams = new URLSearchParams(url.search);
                        if (searchParams.has('stackId')) {
                            const decoded = decodeURIComponent(searchParams.get('stackId'));
                            const parts = decoded.split('/').filter(p => p);
                            const stackIdx = parts.findIndex(p => p.toLowerCase() === 'stack');
                            if (stackIdx >= 0 && parts.length > stackIdx + 1) {
                                stackName = parts[stackIdx + 1];
                            } else {
                                stackName = parts.length > 1 ? parts[parts.length - 2] : (parts.length ? parts[parts.length - 1] : null);
                            }
                        }
                    }
                }

                // If still no stack name, try extracting from document title
                // AWS shows format like "Stack Prod-Something - AWS CloudFormation"
                if (!stackName && document.title) {
                    const titleMatch = document.title.match(/^Stack\s+([^\s-]+(?:-[^\s-]+)*)/i);
                    if (titleMatch && titleMatch[1]) {
                        stackName = titleMatch[1].trim();
                    }
                }

                if (stackName) {
                    newTitle = `[CF] ${formatResourceName(stackName)}`;
                }
            } catch (e) {
                console.error('CloudFormation parsing error:', e);
            }
        }

        // --- Secrets Manager ---
        // Matches URLs like: /secretsmanager/secret?name=%2FStaging%2Fdatabase%2Fstructural-data%2Fservice-admin-credentials
        if (url.pathname.includes("/secretsmanager/secret") || url.pathname.includes("/secretsmanager/")) {
            try {
                const searchParams = new URLSearchParams(url.search);
                const nameParam = searchParams.get('name');
                if (nameParam) {
                    const decoded = decodeURIComponent(nameParam);
                    // Keep the secret's path and add service type
                    newTitle = `[Secret] ${formatResourceName(decoded)}`;
                }
            } catch (e) {
                console.error('Secrets Manager parsing error:', e);
            }
        }

        // --- API Gateway ---
        // Matches URLs like: /apigateway/main/apis/5pqszcma38/resources?api=5pqszcma38
        if (url.pathname.includes("/apigateway/main/apis/")) {
            try {
                // Extract API ID from path
                const apiIdMatch = url.pathname.match(/\/apis\/([^\/]+)/);
                if (apiIdMatch && apiIdMatch[1]) {
                    const apiId = apiIdMatch[1];
                    
                    // Try to get API name from document title
                    // AWS shows format like "INA Event API (5pqszcma38)"
                    const titleMatch = document.title.match(/^(.+?)\s*\([^\)]+\)/);
                    if (titleMatch && titleMatch[1]) {
                        const apiName = titleMatch[1].trim();
                        newTitle = `[API GW] ${formatResourceName(apiName)}`;
                    } else {
                        // Fallback to just API ID
                        newTitle = `[API GW] ${formatResourceName(apiId)}`;
                    }
                }
            } catch (e) {
                console.error('API Gateway parsing error:', e);
            }
        }

        // --- Utilytics ---
        // Matches URLs like: 
        // https://ina-ui.utilytics.com/ina/datahub/dh-21x/e66export/shortTerm/statusStats?...
        // https://me.utilytics.com/me/measurements/00018122-dc90-b176-ea95-7d17a108ee7a
        if (url.hostname.includes('utilytics.com')) {
            try {
                const pathParts = url.pathname.split('/').filter(p => p);
                
                if (pathParts.length > 0) {
                    // Extract service prefix (INA, ME, etc.)
                    const service = pathParts[0].toUpperCase();
                    
                    // Build title from relevant path segments
                    const relevantParts = [];
                    
                    // Skip first part (service name, already used)
                    // Include subsequent meaningful parts
                    for (let i = 1; i < pathParts.length; i++) {
                        const part = pathParts[i];
                        
                        // Stop at common subpage patterns
                        if (['statusStats', 'details', 'edit', 'view', 'settings'].includes(part)) {
                            break;
                        }
                        
                        // Skip UUIDs (GUIDs pattern)
                        if (/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(part)) {
                            break;
                        }
                        
                        relevantParts.push(part);
                    }
                    
                    if (relevantParts.length > 0) {
                        const combined = relevantParts.join(' ');
                        newTitle = `${service} ${formatResourceName(combined)}`;
                    } else {
                        newTitle = service;
                    }
                }
            } catch (e) {
                console.error('Utilytics parsing error:', e);
            }
        }

        // --- Jira / Atlassian ---
        if (url.hostname.includes('atlassian.net')) {
            try {
                // Check if it's a Confluence page
                if (url.pathname.includes('/wiki/')) {
                    favicon = '🟦'; // Blue square for Confluence
                    // Keep the original title as-is (favicon distinguishes it)
                }
                // Handle /issues with JQL queries (personal filters, assignee searches, etc.)
                else if (url.pathname === '/issues' || url.pathname === '/issues/') {
                    favicon = '🟧'; // Orange square for Jira
                    const params = new URLSearchParams(url.search);
                    const jql = params.get('jql');
                    
                    if (jql) {
                        // Helper: try to extract sprint short name from page DOM
                        const getSprintShort = () => {
                            // Look for sprint name pattern like "Farsight 2026-13a" in the page
                            const pageText = document.body ? document.body.innerText : '';
                            const sprintMatch = pageText.match(/Farsight\s+\d{4}-(\d+[a-z]?)/i);
                            return sprintMatch ? sprintMatch[1] : null;
                        };

                        const hasSprint = jql.toLowerCase().includes('sprint');
                        const sprintShort = hasSprint ? getSprintShort() : null;
                            const sprintSuffix = sprintShort ? `${sprintShort}` : '';

                            // Check for multiple assignees (IN clause)
                            if (jql.toLowerCase().includes('assignee in')) {
                                newTitle = sprintSuffix || 'team';
                            }
                            // Single assignee
                            else if (jql.toLowerCase().includes('assignee')) {
                                // Find assignee name from the page DOM
                                const allEls = document.querySelectorAll('[data-testid]');
                                let assigneeName = null;
                                for (const el of allEls) {
                                    const testId = el.getAttribute('data-testid') || '';
                                    if (testId.toLowerCase().includes('assignee')) {
                                        // Look for img alt or nested text
                                        const img = el.querySelector('img[alt]');
                                        if (img && img.alt && img.alt.length > 1) {
                                            assigneeName = img.alt.trim().split(' ')[0].toLowerCase().substring(0, 2);
                                            break;
                                        }
                                        const spans = el.querySelectorAll('span, [role="img"]');
                                        for (const span of spans) {
                                            const txt = span.getAttribute('aria-label') || span.textContent || '';
                                            if (txt.trim().length > 1 && !txt.toLowerCase().includes('assignee')) {
                                                assigneeName = txt.trim().split(' ')[0].toLowerCase().substring(0, 2);
                                                break;
                                            }
                                        }
                                        if (assigneeName) break;
                                    }
                                }
                                newTitle = `${assigneeName || 'ot'}${sprintSuffix}`;
                            } else {
                                newTitle = sprintSuffix || 'filter';
                            }
                        } else {
                            newTitle = `JIRA`;
                        }
                } else if (url.pathname.includes('/jira/') || url.pathname.includes('/browse/')) {
                    favicon = '🟧'; // Orange square for Jira
                    
                    if (url.pathname.includes('/browse/')) {
                        // Extract ticket number from path like /browse/IP1000850-15881
                        const browseMatch = url.pathname.match(/\/browse\/[^/]+-(\d+)/);
                        if (browseMatch) {
                            const ticketNum = browseMatch[1];
                            // Parse DOM for issue title/summary
                            const summaryEl = document.querySelector('[data-testid="issue.views.issue-base.foundation.summary.heading"]')
                                || document.querySelector('h1[data-testid*="summary"]')
                                || document.querySelector('[data-testid*="summary"] h1')
                                || document.querySelector('h1');
                            const summaryText = summaryEl ? summaryEl.textContent.trim() : '';
                            newTitle = summaryText ? `${ticketNum} ${summaryText}` : ticketNum;
                        }
                    } else {
                        const parts = url.pathname.split('/').filter(p => p);
                        const projectsIdx = parts.indexOf('projects');
                        
                        if (projectsIdx >= 0 && parts.length > projectsIdx + 1) {
                            const projectKey = parts[projectsIdx + 1];
                            
                            // If we're on a board view, always show "BOARD"
                            if (parts.includes('boards')) {
                                newTitle = `BOARD`;
                            } else {
                                // For other project pages, check if there's a selected issue
                                const params = new URLSearchParams(url.search);
                                const selectedIssue = params.get('selectedIssue');
                                
                                if (selectedIssue) {
                                    // Keep existing title as-is (favicon distinguishes it)
                                    // No prefix needed - meaningful title is more useful in narrow tabs
                                } else {
                                    newTitle = `${projectKey}`;
                                }
                            }
                        }
                    }
                }
            } catch (e) {
                console.error('Jira parsing error:', e);
            }
        }

        // --- ChatGPT ---
        if (url.hostname === 'chatgpt.com' || url.hostname.endsWith('.chatgpt.com')) {
            newTitle = document.title.replace(/ChatGPT/g, 'Reports');
            removeFavicon();
            replaceBrandingInPageText();
        }

        // --- GitHub ---
        if (url.hostname === 'github.com') {
            const currentTitle = document.title;
            // Strip Jira project prefix (e.g. "IP1000850-16094: ..." -> "16094: ...")
            const jiraMatch = currentTitle.match(/^#?\s*[A-Z][A-Z0-9]+-\d+-(?=\d)/i)
                || currentTitle.match(/^#?\s*[A-Z][A-Z0-9]+-(?=\d)/i);
            if (jiraMatch) {
                const stripped = currentTitle.substring(jiraMatch[0].length);
                newTitle = stripped;
            }
        }

        // Apply new title if changed
        if (newTitle) {
            safeSetTitle(newTitle);
        }
        
        // Apply favicon if changed
        if (favicon) {
            updateFavicon(favicon);
        }
    };

    // --- Observe URL and DOM changes, but debounce updates ---
    const scheduleUpdate = () => {
        clearTimeout(titleUpdateTimer);
        titleUpdateTimer = setTimeout(updateTitle, 300);
    };

    new MutationObserver(scheduleUpdate).observe(document.body, { childList: true, subtree: true });
    // Also observe title/head changes — AWS console sometimes updates document.title directly
    // Observe the <title> element if present, otherwise observe head for child changes
    const titleEl = document.querySelector('head > title');
    if (titleEl) {
        new MutationObserver(scheduleUpdate).observe(titleEl, { characterData: true, childList: true, subtree: true });
    } else {
        new MutationObserver(scheduleUpdate).observe(document.head, { childList: true, subtree: true });
    }
    window.addEventListener("hashchange", scheduleUpdate);
    window.addEventListener("popstate", scheduleUpdate);

    // Run initial update
    updateTitle();
})();
