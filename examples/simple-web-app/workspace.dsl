workspace "Bookshelf" "A simple web app that lets users browse and review books." {

    model {
        reader = person "Reader" "A logged-in user browsing and reviewing books."

        bookshelf = softwareSystem "Bookshelf" "Allows readers to browse a catalogue and post reviews." {
            web = container "Web Application" "Server-rendered UI for browsing and writing reviews." "Next.js"
            api = container "API" "Catalogue and review endpoints." "Node.js"
            db  = container "Database" "Catalogue and review persistence." "Postgres" {
                tags "Data Store"
            }

            reader -> web "Browses and writes reviews via" "HTTPS"
            web    -> api "Calls"                              "HTTPS/JSON"
            api    -> db  "Reads from and writes to"            "SQL/TCP"
        }
    }

    views {
        systemContext bookshelf "SystemContext" {
            include *
            autoLayout lr
        }

        container bookshelf "Containers" {
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
        }
    }
}
