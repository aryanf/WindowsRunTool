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

    const updateTitle = () => {
        const url = new URL(location.href);
        const hash = url.hash || "";
        let newTitle = null;

        // --- SQS ---
        if (hash.includes("#/queues/")) {
            try {
                const encoded = hash.split("#/queues/")[1];
                const decoded = decodeURIComponent(encoded);
                const parts = decoded.split("/");
                const knownSubpages = ["send-receive", "dead-letter-queue", "monitoring", "permissions"];
                let name = parts.pop();
                if (knownSubpages.includes(name) && parts.length > 0) name = parts.pop();
                newTitle = `SQS: ${name}`;
            } catch (e) {
                console.error("SQS parsing error:", e);
            }
        }

        // --- DynamoDB ---
        if (url.pathname.includes("/dynamodbv2/") && hash.includes("table")) {
            try {
                // Match name= parameter in hash
                const nameMatch = hash.match(/name=([^&]+)/);
                if (nameMatch) {
                    const tableName = decodeURIComponent(nameMatch[1]);
                    newTitle = `${tableName}`;
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
                        newTitle = `${bucketName}/${prefix}`;
                    } else {
                        newTitle = `${bucketName}`;
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
                    newTitle = `LG: ${lastPart}`;
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
                    newTitle = `CW: ${lastPart}`;
                }
            } catch (e) {
                console.error("Failed to parse CloudWatch log group name:", e);
            }
        }

        // --- Lambda ---
        // Handle both path-style hashes like `#/functions/FunctionName` and v0 param style
        if (url.pathname.includes("/lambda/") && hash.includes("#/functions")) {
            try {
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
                    newTitle = `λ: ${functionName}`;
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
                    
                    if (servicesIdx >= 0 && parts.length > servicesIdx + 1) {
                        // We have something after "services"
                        let serviceName = parts[servicesIdx + 1];
                        const subpages = ["tasks", "health", "deployments", "metrics", "configuration", "logs", "events"];
                        
                        // If serviceName is NOT a subpage, it's an actual service name
                        if (!subpages.includes(serviceName)) {
                            newTitle = `ECS: ${serviceName}`;
                        } else {
                            // It's a subpage, show cluster name
                            newTitle = `ECS: ${clusterName}`;
                        }
                    } else {
                        // No service in path (just /clusters/name/services or /clusters/name), show cluster
                        newTitle = `ECS: ${clusterName}`;
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
                    newTitle = `EC2: ${instanceId}`;
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
                    newTitle = `LB: ${lbName}`;
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
                    newTitle = `SG: ${sgId}`;
                }
            } catch (e) {
                console.error('Security Group parsing error:', e);
            }
        }

        // --- CloudFormation stack view ---
        // Matches URLs like:
        // #/stacks/stackinfo?filteringText=ina&stackId=arn%3Aaws%3Acloudformation%3A...%2FDev-InA-Manual-Bulk-Sender%2F...
        if (hash.includes("#/stacks/stackinfo") || hash.includes("/stacks/stackinfo")) {
            try {
                // Extract stackId parameter from hash or search
                // Look for stackId=... in the hash
                const stackIdMatch = hash.match(/stackId=([^&]+)/i);
                let stackName = null;
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
                        // fallback: take last non-empty segment
                        stackName = parts.length ? parts[parts.length - 2] || parts[parts.length - 1] : null;
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
                            stackName = parts.length ? parts[parts.length - 2] || parts[parts.length - 1] : null;
                        }
                    }
                }

                if (stackName) {
                    newTitle = `CF: ${stackName}`;
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
                    // Prefix with a key symbol but keep the secret's path as-is
                    newTitle = `🔑 ${decoded}`;
                }
            } catch (e) {
                console.error('Secrets Manager parsing error:', e);
            }
        }

        // Apply new title if changed
        if (newTitle) {
            safeSetTitle(newTitle);
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

    // Initial run
    updateTitle();
})();
