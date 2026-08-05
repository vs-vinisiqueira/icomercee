export interface UserResponse {
  id: number;
  tenant_id: number;
  nome: string;
  email: string;
  role: "admin" | "operador";
  ativo: boolean;
}

export interface SupplierResponse {
  id: number;
  tenant_id: number;
  nome: string;
  contato: string | null;
}

export interface ProductResponse {
  id: number;
  tenant_id: number;
  sku: string;
  nome: string;
  categoria: string | null;
  supplier_id: number | null;
  custo_compra: string;
  preco_venda: string;
  estoque_minimo: number;
  estoque_atual: number;
  ativo: boolean;
}

export interface StockMovementResponse {
  id: number;
  tenant_id: number;
  product_id: number;
  tipo: "entrada" | "saida";
  quantidade: number;
  motivo: string;
  origem: string;
  referencia_pedido_id: number | null;
  custo_unitario: string | null;
  observacao: string | null;
  criado_por: number;
  criado_em: string;
}

export interface OrderResponse {
  id: number;
  tenant_id: number;
  canal: string;
  pedido_id_externo: string;
  item_id_externo: string | null;
  product_id: number | null;
  quantidade: number;
  status: string;
  etiqueta_gerada: boolean;
  etiqueta_url: string | null;
  shipment_id_externo: string | null;
  data_pedido: string | null;
}

export interface ProductMappingResponse {
  id: number;
  tenant_id: number;
  canal: string;
  item_id_externo: string;
  product_id: number;
}

export interface DashboardResponse {
  pedidos_pendentes: OrderResponse[];
  produtos_estoque_baixo: ProductResponse[];
  total_pedidos_pendentes: number;
  total_produtos_estoque_baixo: number;
}

export interface MLCredentialsStatus {
  conectado: boolean;
  ml_user_id: string | null;
  expires_at: string | null;
}
