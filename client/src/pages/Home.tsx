import { useAuth } from "@/_core/hooks/useAuth";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "wouter";
import { Users, Car, Wrench, DollarSign, Plus } from "lucide-react";
import { trpc } from "@/lib/trpc";

export default function Home() {
  const { user, loading, isAuthenticated } = useAuth();
  const { data: clients = [] } = trpc.clients.list.useQuery(undefined, { enabled: isAuthenticated });
  const { data: orders = [] } = trpc.serviceOrders.list.useQuery(undefined, { enabled: isAuthenticated });
  const { data: transactions = [] } = trpc.transactions.list.useQuery(undefined, { enabled: isAuthenticated });

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Carregando...</div>;
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Garageroute66</h1>
          <p className="text-xl text-slate-300 mb-8">Sistema de Gestão de Oficina</p>
          <Button size="lg" asChild>
            <a href={`/api/oauth/login`}>Fazer Login</a>
          </Button>
        </div>
      </div>
    );
  }

  // Calculate financial summary
  const revenues = transactions
    .filter(t => t.type === "revenue")
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);
  
  const expenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);

  const pendingOrders = orders.filter(o => o.status === "pending").length;
  const inProgressOrders = orders.filter(o => o.status === "in_progress").length;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-slate-500 mt-2">Bem-vindo ao Garageroute66, {user?.name}</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="h-4 w-4" />
                Clientes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{clients.length}</div>
              <p className="text-xs text-slate-500 mt-1">Total de clientes cadastrados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Wrench className="h-4 w-4" />
                Ordens de Serviço
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{orders.length}</div>
              <p className="text-xs text-slate-500 mt-1">
                {pendingOrders} pendente{pendingOrders !== 1 ? 's' : ''}, {inProgressOrders} em andamento
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Receitas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {revenues.toFixed(2)}</div>
              <p className="text-xs text-slate-500 mt-1">Total de receitas</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Despesas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">R$ {expenses.toFixed(2)}</div>
              <p className="text-xs text-slate-500 mt-1">Total de despesas</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Ações Rápidas</CardTitle>
              <CardDescription>Acesse as funcionalidades principais</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/clients">
                  <Users className="h-4 w-4 mr-2" />
                  Gerenciar Clientes
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/service-orders">
                  <Wrench className="h-4 w-4 mr-2" />
                  Ordens de Serviço
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/financial">
                  <DollarSign className="h-4 w-4 mr-2" />
                  Financeiro
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Ordens Pendentes</CardTitle>
              <CardDescription>{pendingOrders} ordem{pendingOrders !== 1 ? 's' : ''} aguardando</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                {pendingOrders > 0
                  ? "Existem ordens de serviço pendentes que precisam de atenção."
                  : "Nenhuma ordem pendente no momento."}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Lucro Líquido</CardTitle>
              <CardDescription>Receitas - Despesas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${revenues - expenses >= 0 ? "text-green-600" : "text-red-600"}`}>
                R$ {(revenues - expenses).toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
