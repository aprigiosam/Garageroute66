import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Eye, Trash2 } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Link } from "wouter";

export default function ServiceOrders() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    clientId: "",
    vehicleId: "",
    orderNumber: "",
    description: "",
  });

  const { data: orders = [], refetch } = trpc.serviceOrders.list.useQuery();
  const { data: clients = [] } = trpc.clients.list.useQuery();
  const createMutation = trpc.serviceOrders.create.useMutation();

  const selectedClient = clients.find((c: any) => c.id === parseInt(formData.clientId));
  const { data: vehicles = [] } = trpc.vehicles.listByClient.useQuery(
    { clientId: parseInt(formData.clientId) },
    { enabled: !!formData.clientId }
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await createMutation.mutateAsync({
        clientId: parseInt(formData.clientId),
        vehicleId: parseInt(formData.vehicleId),
        orderNumber: formData.orderNumber,
        description: formData.description,
      });
      
      setFormData({
        clientId: "",
        vehicleId: "",
        orderNumber: "",
        description: "",
      });
      setIsOpen(false);
      refetch();
    } catch (error) {
      console.error("Erro ao criar ordem de serviço:", error);
    }
  };

  const handleDelete = async (id: number) => {
    // TODO: Implementar delete de ordem de serviço
    alert("Funcionalidade de exclusão será implementada em breve");
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Ordens de Serviço</h1>
            <p className="text-slate-500 mt-2">Gerenciar ordens de serviço da oficina</p>
          </div>
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setFormData({
                  clientId: "",
                  vehicleId: "",
                  orderNumber: "",
                  description: "",
                });
              }}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Ordem
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Nova Ordem de Serviço</DialogTitle>
                <DialogDescription>
                  Crie uma nova ordem de serviço para um cliente
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="client">Cliente *</Label>
                  <Select value={formData.clientId} onValueChange={(value) => setFormData({ ...formData, clientId: value, vehicleId: "" })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um cliente" />
                    </SelectTrigger>
                    <SelectContent>
                      {clients.map((client: any) => (
                        <SelectItem key={client.id} value={client.id.toString()}>
                          {client.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {formData.clientId && (
                  <div>
                    <Label htmlFor="vehicle">Veículo *</Label>
                    <Select value={formData.vehicleId} onValueChange={(value) => setFormData({ ...formData, vehicleId: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione um veículo" />
                      </SelectTrigger>
                      <SelectContent>
                        {vehicles.map((vehicle: any) => (
                          <SelectItem key={vehicle.id} value={vehicle.id.toString()}>
                            {vehicle.brand} {vehicle.model} - {vehicle.licensePlate}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <div>
                  <Label htmlFor="orderNumber">Número da OS *</Label>
                  <Input
                    id="orderNumber"
                    value={formData.orderNumber}
                    onChange={(e) => setFormData({ ...formData, orderNumber: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="description">Descrição</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>

                <Button type="submit" className="w-full" disabled={!formData.clientId || !formData.vehicleId || !formData.orderNumber}>
                  Criar Ordem
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {orders.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-slate-500">Nenhuma ordem de serviço cadastrada.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {orders.map((order: any) => (
              <Card key={order.id}>
                <CardContent className="pt-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg">OS #{order.orderNumber}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(order.status)}`}>
                          {getStatusLabel(order.status)}
                        </span>
                      </div>
                      {order.description && <p className="text-sm text-slate-600 mb-2">{order.description}</p>}
                      <p className="text-sm text-slate-600">
                        Valor Total: <span className="font-medium">R$ {parseFloat(order.totalPrice).toFixed(2)}</span>
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/service-orders/${order.id}`}>
                          <Eye className="h-4 w-4" />
                        </Link>
                      </Button>

                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
