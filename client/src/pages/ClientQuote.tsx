import { useParams } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, ArrowLeft } from "lucide-react";
import { trpc } from "@/lib/trpc";
import { Link } from "wouter";

export default function ClientQuote() {
  const { id } = useParams<{ id: string }>();
  const orderId = parseInt(id || "0");
  
  const { data: order } = trpc.serviceOrders.get.useQuery({ id: orderId });
  const { data: items = [] } = trpc.serviceOrderItems.list.useQuery({ serviceOrderId: orderId });
  const { data: client } = trpc.clients.get.useQuery({ id: order?.clientId || 0 }, { enabled: !!order?.clientId });
  const { data: vehicle } = trpc.vehicles.get.useQuery({ id: order?.vehicleId || 0 }, { enabled: !!order?.vehicleId });

  if (!order) {
    return (
      <div className="min-h-screen bg-slate-50 p-8">
        <div className="text-center py-12">
          <p>Orçamento não encontrado</p>
        </div>
      </div>
    );
  }

  const totalPrice = items.reduce((sum, item) => sum + (parseFloat(item.unitPrice) * item.quantity), 0);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* Header with Print Button */}
        <div className="mb-6 flex justify-between items-center no-print">
          <Button variant="outline" asChild>
            <Link href="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar
            </Link>
          </Button>
          <Button onClick={handlePrint}>
            <Download className="h-4 w-4 mr-2" />
            Imprimir / Salvar PDF
          </Button>
        </div>

        {/* Quote Document */}
        <Card className="shadow-lg">
          <CardHeader className="border-b bg-slate-900 text-white">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold">ORÇAMENTO</h1>
                <p className="text-slate-300 mt-2">Nº {order.orderNumber}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-300">Data:</p>
                <p className="font-semibold">{new Date(order.createdAt).toLocaleDateString('pt-BR')}</p>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-8 space-y-8">
            {/* Client Info */}
            <div className="grid grid-cols-2 gap-8">
              <div>
                <h3 className="text-sm font-semibold text-slate-600 mb-2">CLIENTE</h3>
                <p className="text-lg font-semibold">{client?.name}</p>
                {client?.email && <p className="text-sm text-slate-600">{client.email}</p>}
                {client?.phone && <p className="text-sm text-slate-600">{client.phone}</p>}
                {client?.address && <p className="text-sm text-slate-600">{client.address}</p>}
                {client?.city && (
                  <p className="text-sm text-slate-600">
                    {client.city}, {client.state} {client.zipCode}
                  </p>
                )}
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-600 mb-2">VEÍCULO</h3>
                <p className="text-lg font-semibold">
                  {vehicle?.brand} {vehicle?.model}
                </p>
                {vehicle?.year && <p className="text-sm text-slate-600">Ano: {vehicle.year}</p>}
                <p className="text-sm text-slate-600">Placa: {vehicle?.licensePlate}</p>
                {vehicle?.color && <p className="text-sm text-slate-600">Cor: {vehicle.color}</p>}
              </div>
            </div>

            {/* Description */}
            {order.description && (
              <div className="bg-slate-50 p-4 rounded border border-slate-200">
                <h3 className="text-sm font-semibold text-slate-600 mb-2">DESCRIÇÃO DO SERVIÇO</h3>
                <p className="text-slate-700">{order.description}</p>
              </div>
            )}

            {/* Items Table */}
            <div>
              <h3 className="text-sm font-semibold text-slate-600 mb-4">ITENS DO ORÇAMENTO</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-slate-900">
                      <th className="text-left py-3 px-4 font-semibold">DESCRIÇÃO</th>
                      <th className="text-center py-3 px-4 font-semibold">TIPO</th>
                      <th className="text-right py-3 px-4 font-semibold">QUANTIDADE</th>
                      <th className="text-right py-3 px-4 font-semibold">VALOR UNITÁRIO</th>
                      <th className="text-right py-3 px-4 font-semibold">SUBTOTAL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item: any, index: number) => (
                      <tr key={item.id} className={index % 2 === 0 ? "bg-slate-50" : ""}>
                        <td className="py-3 px-4">{item.description}</td>
                        <td className="text-center py-3 px-4">
                          <span className="text-xs bg-slate-200 px-2 py-1 rounded">
                            {item.type === "part" ? "Peça" : "Serviço"}
                          </span>
                        </td>
                        <td className="text-right py-3 px-4">{item.quantity}</td>
                        <td className="text-right py-3 px-4">R$ {parseFloat(item.unitPrice).toFixed(2)}</td>
                        <td className="text-right py-3 px-4 font-semibold">
                          R$ {(parseFloat(item.unitPrice) * item.quantity).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Total */}
            <div className="flex justify-end">
              <div className="w-80 border-t-2 border-slate-900 pt-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-slate-600">Subtotal:</span>
                  <span>R$ {totalPrice.toFixed(2)}</span>
                </div>
                <div className="flex justify-between items-center mb-4">
                  <span className="text-slate-600">Impostos (0%):</span>
                  <span>R$ 0.00</span>
                </div>
                <div className="flex justify-between items-center text-xl font-bold bg-slate-900 text-white p-4 rounded">
                  <span>TOTAL:</span>
                  <span>R$ {totalPrice.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="border-t pt-6 text-center text-sm text-slate-600">
              <p className="mb-2">
                Este orçamento é válido por 7 dias a partir da data acima.
              </p>
              <p>
                Para dúvidas ou alterações, entre em contato conosco.
              </p>
              <p className="mt-4 font-semibold text-slate-900">
                Garageroute66 - Oficina Mecânica
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Print Styles */}
      <style>{`
        @media print {
          body {
            background: white;
            padding: 0;
            margin: 0;
          }
          .no-print {
            display: none;
          }
          .shadow-lg {
            box-shadow: none;
          }
        }
      `}</style>
    </div>
  );
}
