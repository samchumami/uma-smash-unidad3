variable "region" { default = "us-east-1" }
variable "nodos_juego" {
  description = "Nodos iniciales del pool de servidores de juego"
  default     = 3
}
variable "tipo_nodo" { default = "c7i.xlarge" }
