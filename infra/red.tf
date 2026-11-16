# Red: VPC con subredes publicas (los servidores de Agones necesitan IP publica).
# Sin NAT Gateway para no pagarlo en el laboratorio.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name                    = "uma-vpc"
  cidr                    = "10.0.0.0/16"
  azs                     = ["${var.region}a", "${var.region}b"]
  public_subnets          = ["10.0.1.0/24", "10.0.2.0/24"]
  map_public_ip_on_launch = true
  enable_nat_gateway      = false
}
