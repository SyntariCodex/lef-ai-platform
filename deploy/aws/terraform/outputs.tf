output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.lef.dns_name
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.lef.name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.main.repository_url
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "The IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  description = "The IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "cloudwatch_log_group" {
  description = "The name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.name
} 