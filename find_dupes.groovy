#!/usr/bin/env groovy

import groovy.json.JsonOutput

def libraryDir = new File("path/to/your/shared-library")
def varsDir = new File(libraryDir, "vars")
def duplicates = [:].withDefault { [] }

// Step 1: Find all .groovy files in vars/
varsDir.eachFile { file ->
    if (file.name.endsWith('.groovy')) {
        def content = file.text
        
        // Extract call() methods (simplified regex)
        def methods = (content =~ /def\s+(call|[\w]+)\s*\(([^)]*)\)\s*\{([^\}]*)\}/)
        
        methods.each { match ->
            def methodName = match[1]
            def methodBody = match[3].trim()
            duplicates[methodBody] << "${file.name}:${methodName}"
        }
    }
}

// Step 2: Filter real duplicates (same body in 2+ files)
def realDuplicates = duplicates.findAll { k, v -> v.size() > 1 }

// Generate report
new File("duplication_report.html").withWriter { writer ->
    writer << """
    <html><body>
    <h1>Shared Library Duplication Report</h1>
    <p>Scanned ${varsDir.listFiles().size()} files in vars/</p>
    <h2>${realDuplicates.size()} Duplicate Functions Found</h2>
    <table border="1">
    <tr><th>Function Body Hash</th><th>Locations</th><th>Sample Code</th></tr>
    """
    
    realDuplicates.each { body, locations ->
        writer << """
        <tr>
            <td>${body.hashCode()}</td>
            <td>${locations.join('<br>')}</td>
            <td><pre>${body.take(200).escapeHtml()}</pre></td>
        </tr>
        """
    }
    
    writer << "</table></body></html>"
}

println "Report generated: duplication_report.html"