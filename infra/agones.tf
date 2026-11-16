data "aws_eks_cluster_auth" "actual" {
  name = module.eks.cluster_name
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    token                  = data.aws_eks_cluster_auth.actual.token
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  }
}

resource "helm_release" "agones" {
  name             = "agones"
  repository       = "https://agones.dev/chart/stable"
  chart            = "agones"
  namespace        = "agones-system"
  create_namespace = true
  depends_on       = [module.eks]
}
