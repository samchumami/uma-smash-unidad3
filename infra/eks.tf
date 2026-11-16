module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name                             = "uma-${terraform.workspace}"
  cluster_version                          = "1.35" # Agones soporta 1.34-1.36
  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true
  vpc_id                                   = module.vpc.vpc_id
  subnet_ids                               = module.vpc.public_subnets

  # Tu usuario de AWS tambien administra el cluster (ademas del rol con el que corre Terraform)
  access_entries = {
    alumno = {
      principal_arn = "arn:aws:iam::493667572687:user/admin_25460312"
      policy_associations = {
        admin = {
          policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = { type = "cluster" }
        }
      }
    }
  }

  # Firewall de los servidores de juego (equivale a nebula-gameservers de la guia)
  node_security_group_additional_rules = {
    juego_tcp = { type = "ingress", protocol = "tcp", from_port = 7000, to_port = 8000, cidr_blocks = ["0.0.0.0/0"] }
    juego_udp = { type = "ingress", protocol = "udp", from_port = 7000, to_port = 8000, cidr_blocks = ["0.0.0.0/0"] }
  }

  eks_managed_node_groups = {
    juego = {
      ami_type       = "AL2023_x86_64_STANDARD" # Kubernetes 1.33+ ya no tiene AMIs AL2
      instance_types = [var.tipo_nodo]
      min_size       = 3
      max_size       = 12
      desired_size   = var.nodos_juego
      labels         = { rol = "juego" }
      # Permisos para que el Cluster Autoscaler agregue/quite nodos (practica 3.4)
      iam_role_additional_policies = { autoscaler = aws_iam_policy.autoscaler.arn }
    }
  }
}

resource "aws_iam_policy" "autoscaler" {
  name = "uma-${terraform.workspace}-cluster-autoscaler"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "autoscaling:DescribeAutoScalingGroups", "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:DescribeLaunchConfigurations", "autoscaling:DescribeScalingActivities",
        "autoscaling:DescribeTags", "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup",
        "ec2:DescribeImages", "ec2:DescribeInstanceTypes", "ec2:DescribeLaunchTemplateVersions",
        "ec2:GetInstanceTypesFromInstanceRequirements", "eks:DescribeNodegroup"
      ]
      Resource = "*"
    }]
  })
}

resource "aws_ecr_repository" "imagenes" {
  name         = "uma-server"
  force_delete = true # permite terraform destroy aunque tenga imagenes
}
