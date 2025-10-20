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
        if (url.pathname.includes("/lambda/") && hash.includes("#/functions")) {
            try {
                // Check for function name in v0 parameter
                const v0Match = hash.match(/v0=([^&]+)/);
                if (v0Match) {
                    const functionName = decodeURIComponent(v0Match[1]);
                    newTitle = `${functionName}`;
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
                            newTitle = `${serviceName}`;
                        } else {
                            // It's a subpage, show cluster name
                            newTitle = `${clusterName}`;
                        }
                    } else {
                        // No service in path (just /clusters/name/services or /clusters/name), show cluster
                        newTitle = `${clusterName}`;
                    }
                }
            } catch (e) {
                console.error("ECS parsing error:", e);
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
    window.addEventListener("hashchange", scheduleUpdate);
    window.addEventListener("popstate", scheduleUpdate);

    // Initial run
    updateTitle();
})();
