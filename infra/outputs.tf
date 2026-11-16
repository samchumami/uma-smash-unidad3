output "cluster" { value = module.eks.cluster_name }
output "registro" { value = aws_ecr_repository.imagenes.repository_url }
