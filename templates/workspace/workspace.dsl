workspace "{{PROJECT_NAME}}" "Architecture of {{PROJECT_NAME}}." {

    !docs docs
    !adrs adrs

    model {
        user = person "User" "An end user of the system."

        system = softwareSystem "{{PROJECT_NAME}}" "The system being modelled." {
            webapp = container "Web Application" "Serves the UI." "Next.js"
            api    = container "API" "Handles business logic." "Node.js"
            db     = container "Database" "Stores application state." "Postgres" {
                tags "Data Store"
            }

            user   -> webapp "Uses" "HTTPS"
            webapp -> api    "Calls" "HTTPS/JSON"
            api    -> db     "Reads from and writes to" "SQL/TCP"
        }
    }

    views {
        systemContext system "SystemContext" {
            include *
            autoLayout lr
        }

        container system "Containers" {
            include *
            autoLayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Data Store" {
                shape Cylinder
            }
            element "External" {
                background #999999
                color #ffffff
            }
        }
    }
}
