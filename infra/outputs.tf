output "cluster" { value = module.eks.cluster_name }
output "registro" { value = aws_ecr_repository.imagenes.repository_url }
output "kubeconfig" { value = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.region}" }
