import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Edit2, Trash2, ArrowLeft } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Link, useParams } from "wouter";

export default function ClientDetail() {
  const { id } = useParams<{ id: string }>();
  const clientId = parseInt(id || "0");
  
  const [isOpen, setIsOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    brand: "",
    model: "",
    year: "",
    licensePlate: "",
    vin: "",
    color: "",
  });

  const { data: client } = trpc.clients.get.useQuery({ id: clientId });
  const { data: vehicles = [], refetch } = trpc.vehicles.listByClient.useQuery({ clientId });
  const { data: orders = [] } = trpc.serviceOrders.listByClient.useQuery({ clientId });
  
  const createMutation = trpc.vehicles.create.useMutation();
  const updateMutation = trpc.vehicles.update.useMutation();
  const deleteMutation = trpc.vehicles.delete.useMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingId) {
        await updateMutation.mutateAsync({
          id: editingId,
          brand: formData.brand,
          model: formData.model,
          year: formData.year ? parseInt(formData.year) : undefined,
          licensePlate: formData.licensePlate,
          vin: formData.vin,
          color: formData.color,
        });
      } else {
        await createMutation.mutateAsync({
          clientId,
          brand: formData.brand,
          model: formData.model,
          year: formData.year ? parseInt(formData.year) : undefined,
          licensePlate: formData.licensePlate,
          vin: formData.vin,
          color: formData.color,
        });
      }
      
      setFormData({
        brand: "",
        model: "",
        year: "",
        licensePlate: "",
        vin: "",
        color: "",
      });
      setEditingId(null);
      setIsOpen(false);
      refetch();
    } catch (error) {
      console.error("Erro ao salvar veículo:", error);
    }
  };

  const handleEdit = (vehicle: any) => {
    setFormData({
      brand: vehicle.brand || "",
      model: vehicle.model || "",
      year: vehicle.year?.toString() || "",
      licensePlate: vehicle.licensePlate || "",
      vin: vehicle.vin || "",
      color: vehicle.color || "",
    });
    setEditingId(vehicle.id);
    setIsOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja deletar este veículo?")) {
      try {
        await deleteMutation.mutateAsync({ id });
        refetch();
      } catch (error) {
        console.error("Erro ao deletar veículo:", error);
      }
    }
  };

  if (!client) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p>Cliente não encontrado</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" asChild>
            <Link href="/clients">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{client.name}</h1>
            <p className="text-slate-500 mt-2">Detalhes do cliente e seus veículos</p>
          </div>
        </div>

        {/* Client Info */}
        <Card>
          <CardHeader>
            <CardTitle>Informações do Cliente</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {client.email && (
                <div>
                  <p className="text-sm text-slate-500">Email</p>
                  <p className="font-medium">{client.email}</p>
                </div>
              )}
              {client.phone && (
                <div>
                  <p className="text-sm text-slate-500">Telefone</p>
                  <p className="font-medium">{client.phone}</p>
                </div>
              )}
              {client.cpf && (
                <div>
                  <p className="text-sm text-slate-500">CPF</p>
                  <p className="font-medium">{client.cpf}</p>
                </div>
              )}
              {client.address && (
                <div>
                  <p className="text-sm text-slate-500">Endereço</p>
                  <p className="font-medium">{client.address}</p>
                </div>
              )}
              {client.city && (
                <div>
                  <p className="text-sm text-slate-500">Cidade</p>
                  <p className="font-medium">{client.city}, {client.state}</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Vehicles */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Veículos ({vehicles.length})</h2>
            <Dialog open={isOpen} onOpenChange={setIsOpen}>
              <DialogTrigger asChild>
                <Button onClick={() => {
                  setEditingId(null);
                  setFormData({
                    brand: "",
                    model: "",
                    year: "",
                    licensePlate: "",
                    vin: "",
                    color: "",
                  });
                }}>
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Veículo
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>{editingId ? "Editar Veículo" : "Novo Veículo"}</DialogTitle>
                  <DialogDescription>
                    {editingId ? "Atualize os dados do veículo" : "Adicione um novo veículo para este cliente"}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="brand">Marca *</Label>
                      <Input
                        id="brand"
                        value={formData.brand}
                        onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="model">Modelo *</Label>
                      <Input
                        id="model"
                        value={formData.model}
                        onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="year">Ano</Label>
                      <Input
                        id="year"
                        type="number"
                        value={formData.year}
                        onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="color">Cor</Label>
                      <Input
                        id="color"
                        value={formData.color}
                        onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="licensePlate">Placa *</Label>
                    <Input
                      id="licensePlate"
                      value={formData.licensePlate}
                      onChange={(e) => setFormData({ ...formData, licensePlate: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="vin">VIN</Label>
                    <Input
                      id="vin"
                      value={formData.vin}
                      onChange={(e) => setFormData({ ...formData, vin: e.target.value })}
                    />
                  </div>
                  <Button type="submit" className="w-full">
                    {editingId ? "Atualizar" : "Criar"} Veículo
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {vehicles.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-slate-500">Nenhum veículo cadastrado para este cliente.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {vehicles.map((vehicle: any) => (
                <Card key={vehicle.id}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg">
                          {vehicle.brand} {vehicle.model} {vehicle.year && `(${vehicle.year})`}
                        </h3>
                        <p className="text-sm text-slate-600">Placa: {vehicle.licensePlate}</p>
                        {vehicle.color && <p className="text-sm text-slate-600">Cor: {vehicle.color}</p>}
                        {vehicle.vin && <p className="text-sm text-slate-600">VIN: {vehicle.vin}</p>}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(vehicle)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(vehicle.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Service History */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Histórico de Serviços ({orders.length})</h2>
          {orders.length === 0 ? (
            <Card>
              <CardContent className="pt-6">
                <p className="text-center text-slate-500">Nenhuma ordem de serviço para este cliente.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {orders.map((order: any) => (
                <Card key={order.id}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-semibold">OS #{order.orderNumber}</h3>
                        <p className="text-sm text-slate-600">{order.description}</p>
                        <p className="text-sm text-slate-600">Status: <span className="font-medium">{order.status}</span></p>
                      </div>
                      <Button variant="outline" size="sm" asChild>
                        <Link href={`/service-orders/${order.id}`}>
                          Ver Detalhes
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
