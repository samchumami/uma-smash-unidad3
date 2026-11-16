# El repositorio ECR ya existia (practicas 3.2 y 3.3): se adopta en el estado de Terraform en lugar de crearlo.
import {
  to = aws_ecr_repository.imagenes
  id = "uma-server"
}
