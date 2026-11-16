module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name                             = "uma-${terraform.workspace}"
  cluster_version                          = "1.35" # Agones soporta 1.34-1.36
  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true
  vpc_id                                   = module.vpc.vpc_id
  subnet_ids                               = module.vpc.public_subnets

  # Firewall de los servidores de juego (equivale a nebula-gameservers de la guia)
  node_security_group_additional_rules = {
    juego_tcp = { type = "ingress", protocol = "tcp", from_port = 7000, to_port = 8000, cidr_blocks = ["0.0.0.0/0"] }
    juego_udp = { type = "ingress", protocol = "udp", from_port = 7000, to_port = 8000, cidr_blocks = ["0.0.0.0/0"] }
  }

  eks_managed_node_groups = {
    juego = {
      instance_types = [var.tipo_nodo]
      min_size       = 3
      max_size       = 20
      desired_size   = var.nodos_juego
      labels         = { rol = "juego" }
    }
  }
}

resource "aws_ecr_repository" "imagenes" {
  name         = "uma-server"
  force_delete = true # permite terraform destroy aunque tenga imagenes
}
