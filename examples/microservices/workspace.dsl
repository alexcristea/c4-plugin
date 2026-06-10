workspace "ShopCo" "Online retailer composed of multiple services and an event bus." {

    model {
        customer = person "Customer" "Browses products and places orders."
        opsAgent = person "Operations Agent" "Handles fulfilment and refunds."

        stripe = softwareSystem "Stripe" "Payment processing." {
            tags "External"
        }
        sendgrid = softwareSystem "SendGrid" "Transactional email." {
            tags "External"
        }

        shop = softwareSystem "ShopCo" "Storefront, ordering, and back-office." {
            storefront = container "Storefront" "Customer-facing storefront." "Next.js"
            backoffice = container "Back Office" "Internal ops console." "React"
            catalog    = container "Catalog Service" "Product catalogue API." "Go"
            orders     = container "Order Service" "Order lifecycle and persistence." "Java/Spring Boot"
            payments   = container "Payment Service" "Talks to the payment gateway." "Node.js"
            notify     = container "Notification Service" "Emails customers about order events." "Python"
            events     = container "Event Bus" "Asynchronous events between services." "Kafka" {
                tags "Event Bus"
            }
            catalogDb  = container "Catalog DB" "Products and inventory." "Postgres" {
                tags "Data Store"
            }
            ordersDb   = container "Orders DB" "Order history and state." "Postgres" {
                tags "Data Store"
            }

            customer   -> storefront "Browses, places orders via" "HTTPS"
            opsAgent   -> backoffice "Manages orders via"          "HTTPS"

            storefront -> catalog    "Reads products from"         "HTTPS/JSON"
            storefront -> orders     "Places orders via"           "HTTPS/JSON"
            backoffice -> orders     "Manages orders via"          "HTTPS/JSON"

            catalog    -> catalogDb  "Reads/writes"                "SQL/TCP"
            orders     -> ordersDb   "Reads/writes"                "SQL/TCP"

            orders     -> payments   "Requests payment via"        "HTTPS/JSON"
            payments   -> stripe     "Charges via"                 "HTTPS/JSON"

            orders     -> events     "Publishes order events to"   "Kafka protocol"
            events     -> notify     "Delivers events to"          "Kafka protocol"
            notify     -> sendgrid   "Sends emails via"            "HTTPS/JSON"
        }

        deploymentEnvironment "Production" {
            deploymentNode "AWS eu-west-1" "Production region." "AWS" {
                deploymentNode "EKS" "" "Kubernetes" {
                    storefrontInstance = containerInstance storefront
                    backofficeInstance = containerInstance backoffice
                    catalogInstance    = containerInstance catalog
                    ordersInstance     = containerInstance orders
                    paymentsInstance   = containerInstance payments
                    notifyInstance     = containerInstance notify
                }
                deploymentNode "MSK" "" "Managed Kafka" {
                    eventsInstance = containerInstance events
                }
                deploymentNode "RDS — Catalog" "" "Postgres" {
                    catalogDbInstance = containerInstance catalogDb
                }
                deploymentNode "RDS — Orders" "" "Postgres" {
                    ordersDbInstance = containerInstance ordersDb
                }
                infrastructureNode "ALB" "Internet-facing load balancer." "AWS ALB" {
                    -> storefrontInstance "Routes requests to" "HTTPS"
                    -> backofficeInstance "Routes requests to" "HTTPS"
                }
            }
        }
    }

    views {
        systemLandscape "Landscape" {
            include *
            autoLayout lr
        }

        systemContext shop "ShopContext" {
            include *
            autoLayout lr
        }

        container shop "Containers" {
            include *
            autoLayout lr
        }

        deployment shop "Production" "ProductionDeployment" {
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
            element "Event Bus" {
                shape Pipe
            }
            element "External" {
                background #999999
                color #ffffff
            }
        }
    }
}
