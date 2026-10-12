workspace "Bookstore on AWS" "A web shop deployed to AWS, styled with the Structurizr AWS theme." {

    model {
        customer = person "Customer" "Browses and buys books."

        bookstore = softwareSystem "Bookstore" "Sells books online." {
            webApp = container "Web App" "Serves the storefront and checkout API." "Node.js"
            database = container "Database" "Stores catalogue and orders." "Postgres" {
                tags "Database"
            }
            assets = container "Asset Store" "Holds book cover images." "Amazon S3" {
                tags "Database"
            }
        }

        customer -> webApp "Browses and buys books using" "HTTPS"
        webApp -> database "Reads from and writes to" "SQL/TLS"
        webApp -> assets "Reads cover images from" "HTTPS"

        production = deploymentEnvironment "Production" {
            deploymentNode "Amazon Web Services" "" "AWS" {
                tags "Amazon Web Services - AWS Cloud"

                deploymentNode "eu-west-1" "" "AWS Region" {
                    tags "Amazon Web Services - Region"

                    dns = infrastructureNode "DNS" "Routes bookstore.example.com to the load balancer." "Amazon Route 53" {
                        tags "Amazon Web Services - Route 53"
                    }
                    loadBalancer = infrastructureNode "Load Balancer" "Terminates TLS and spreads traffic across tasks." "Application Load Balancer" {
                        tags "Amazon Web Services - Load Balancing"
                    }

                    deploymentNode "VPC" "" "Amazon VPC" {
                        tags "Amazon Web Services - Virtual Private Cloud"

                        deploymentNode "ECS Cluster" "" "Amazon ECS" {
                            tags "Amazon Web Services - Elastic Container Service"

                            deploymentNode "Fargate Task" "" "AWS Fargate" "" 2 {
                                tags "Amazon Web Services - Fargate"
                                webAppInstance = containerInstance webApp
                            }
                        }

                        deploymentNode "Database Server" "" "Amazon RDS for PostgreSQL" {
                            tags "Amazon Web Services - RDS"
                            containerInstance database
                        }
                    }

                    deploymentNode "Bucket" "" "Amazon S3" {
                        tags "Amazon Web Services - Simple Storage Service"
                        containerInstance assets
                    }
                }
            }

            dns -> loadBalancer "Forwards requests to" "HTTPS"
            loadBalancer -> webAppInstance "Forwards requests to" "HTTPS"
        }
    }

    views {
        systemContext bookstore "Context" {
            include *
            autoLayout lr
        }

        container bookstore "Containers" {
            include *
            autoLayout lr
        }

        deployment bookstore production "Production" {
            include *
            autoLayout lr
        }

        styles {
            element "Database" {
                shape cylinder
            }
        }

        theme amazon-web-services-2025.07
    }

}
