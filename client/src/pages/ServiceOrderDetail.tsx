import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Edit2, Trash2, ArrowLeft, Download } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Link, useParams } from "wouter";

export default function ServiceOrderDetail() {
  const { id } = useParams<{ id: string }>();
  const orderId = parseInt(id || "0");
  
  const [isOpen, setIsOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    description: "",
    type: "part" as "part" | "service",
    quantity: "1",
    unitCost: "",
    unitPrice: "",
  });

  const { data: order } = trpc.serviceOrders.get.useQuery({ id: orderId });
  const { data: items = [], refetch } = trpc.serviceOrderItems.list.useQuery({ serviceOrderId: orderId });
  const { data: client } = trpc.clients.get.useQuery({ id: order?.clientId || 0 }, { enabled: !!order?.clientId });
  const { data: vehicle } = trpc.vehicles.get.useQuery({ id: order?.vehicleId || 0 }, { enabled: !!order?.vehicleId });
  
  const createMutation = trpc.serviceOrderItems.create.useMutation();
  const updateMutation = trpc.serviceOrderItems.update.useMutation();
  const deleteMutation = trpc.serviceOrderItems.delete.useMutation();
  const updateStatusMutation = trpc.serviceOrders.updateStatus.useMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingId) {
        await updateMutation.mutateAsync({
          id: editingId,
          serviceOrderId: orderId,
          description: formData.description,
          type: formData.type,
          quantity: parseInt(formData.quantity),
          unitCost: formData.unitCost,
          unitPrice: formData.unitPrice,
        });
      } else {
        await createMutation.mutateAsync({
          serviceOrderId: orderId,
          description: formData.description,
          type: formData.type,
          quantity: parseInt(formData.quantity),
          unitCost: formData.unitCost,
          unitPrice: formData.unitPrice,
        });
      }
      
      setFormData({
        description: "",
        type: "part",
        quantity: "1",
        unitCost: "",
        unitPrice: "",
      });
      setEditingId(null);
      setIsOpen(false);
      refetch();
    } catch (error) {
      console.error("Erro ao salvar item:", error);
    }
  };

  const handleEdit = (item: any) => {
    setFormData({
      description: item.description,
      type: item.type,
      quantity: item.quantity.toString(),
      unitCost: item.unitCost,
      unitPrice: item.unitPrice,
    });
    setEditingId(item.id);
    setIsOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja deletar este item?")) {
      try {
        await deleteMutation.mutateAsync({ id, serviceOrderId: orderId });
        refetch();
      } catch (error) {
        console.error("Erro ao deletar item:", error);
      }
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    try {
      await updateStatusMutation.mutateAsync({
        id: orderId,
        status: newStatus as any,
      });
    } catch (error) {
      console.error("Erro ao atualizar status:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      case "in_progress":
        return "bg-blue-100 text-blue-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "paid":
        return "bg-purple-100 text-purple-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: "Pendente",
      in_progress: "Em Andamento",
      completed: "Concluída",
      paid: "Paga",
      cancelled: "Cancelada",
    };
    return labels[status] || status;
  };

  if (!order) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p>Ordem de serviço não encontrada</p>
        </div>
      </DashboardLayout>
    );
  }

  const totalCost = items.reduce((sum, item) => sum + (parseFloat(item.unitCost) * item.quantity), 0);
  const totalPrice = items.reduce((sum, item) => sum + (parseFloat(item.unitPrice) * item.quantity), 0);
  const profit = totalPrice - totalCost;
  const profitMargin = totalPrice > 0 ? ((profit / totalPrice) * 100).toFixed(1) : "0";

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" asChild>
            <Link href="/service-orders">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold tracking-tight">OS #{order.orderNumber}</h1>
            <p className="text-slate-500 mt-2">Detalhes da ordem de serviço</p>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link href={`/quote/${orderId}`}>
              <Download className="h-4 w-4 mr-2" />
              Gerar Orçamento
            </Link>
          </Button>
        </div>

        {/* Order Header Info */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Informações da Ordem</CardTitle>
                <CardDescription>Dados do cliente e veículo</CardDescription>
              </div>
              <Select value={order.status} onValueChange={handleStatusChange}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">Pendente</SelectItem>
                  <SelectItem value="in_progress">Em Andamento</SelectItem>
                  <SelectItem value="completed">Concluída</SelectItem>
                  <SelectItem value="paid">Paga</SelectItem>
                  <SelectItem value="cancelled">Cancelada</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-slate-500">Cliente</p>
                <p className="font-medium">{client?.name}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">Veículo</p>
                <p className="font-medium">
                  {vehicle?.brand} {vehicle?.model} - {vehicle?.licensePlate}
                </p>
              </div>
              {order.description && (
                <div className="col-span-2">
                  <p className="text-sm text-slate-500">Descrição</p>
                  <p className="font-medium">{order.description}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Items */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Itens da Ordem ({items.length})</h2>
            <Dialog open={isOpen} onOpenChange={setIsOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  setEditingId(null);
                  setFormData({
                    description: "",
                    type: "part",
                    quantity: "1",
                    unitCost: "",
                    unitPrice: "",
                  });
                }}>
                  <Plus className="h-4 w-4 mr-2" />
                  Adicionar Item
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editingId ? "Editar Item" : "Novo Item"}</DialogTitle>
                  <DialogDescription>
                    {editingId ? "Atualize os dados do item" : "Adicione um item à ordem de serviço"}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="description">Descrição *</Label>
                    <Input
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="type">Tipo *</Label>
                      <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value as any })}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="part">Peça</SelectItem>
                          <SelectItem value="service">Serviço</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="quantity">Quantidade *</Label>
                      <Input
                        id="quantity"
                        type="number"
                        value={formData.quantity}
                        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="unitCost">Custo Unitário *</Label>
                      <Input
                        id="unitCost"
                        type="number"
                        step="0.01"
                        value={formData.unitCost}
                        onChange={(e) => setFormData({ ...formData, unitCost: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="unitPrice">Preço Unitário *</Label>
                      <Input
                        id="unitPrice"
                        type="number"
                        step="0.01"
                        value={formData.unitPrice}
                        onChange={(e) => setFormData({ ...formData, unitPrice: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <Button type="submit" className="w-full">
                    {editingId ? "Atualizar" : "Adicionar"} Item
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {items.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-slate-500">Nenhum item adicionado a esta ordem.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2 px-4">Descrição</th>
                      <th className="text-left py-2 px-4">Tipo</th>
                      <th className="text-right py-2 px-4">Qtd</th>
                      <th className="text-right py-2 px-4">Custo Unit.</th>
                      <th className="text-right py-2 px-4">Preço Unit.</th>
                      <th className="text-right py-2 px-4">Subtotal</th>
                      <th className="text-center py-2 px-4">Ações</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item: any) => (
                      <tr key={item.id} className="border-b hover:bg-slate-50">
                        <td className="py-2 px-4">{item.description}</td>
                        <td className="py-2 px-4">
                          <span className="text-xs bg-slate-100 px-2 py-1 rounded">
                            {item.type === "part" ? "Peça" : "Serviço"}
                          </span>
                        </td>
                        <td className="text-right py-2 px-4">{item.quantity}</td>
                        <td className="text-right py-2 px-4">R$ {parseFloat(item.unitCost).toFixed(2)}</td>
                        <td className="text-right py-2 px-4">R$ {parseFloat(item.unitPrice).toFixed(2)}</td>
                        <td className="text-right py-2 px-4 font-medium">
                          R$ {(parseFloat(item.unitPrice) * item.quantity).toFixed(2)}
                        </td>
                        <td className="text-center py-2 px-4">
                          <div className="flex gap-2 justify-center">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEdit(item)}
                            >
                              <Edit2 className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(item.id)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Summary */}
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-2 text-right">
                    <div className="flex justify-end gap-4">
                      <span className="text-slate-600">Custo Total:</span>
                      <span className="font-medium w-32">R$ {totalCost.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-end gap-4 border-t pt-2">
                      <span className="text-slate-600">Preço Total (Cliente):</span>
                      <span className="font-bold w-32 text-lg">R$ {totalPrice.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-end gap-4 border-t pt-2">
                      <span className="text-slate-600">Lucro:</span>
                      <span className={`font-bold w-32 ${profit >= 0 ? "text-green-600" : "text-red-600"}`}>
                        R$ {profit.toFixed(2)} ({profitMargin}%)
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
