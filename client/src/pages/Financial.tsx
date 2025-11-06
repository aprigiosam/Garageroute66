import { useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, TrendingUp, TrendingDown } from "lucide-react";
import { trpc } from "@/lib/trpc";

export default function Financial() {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    type: "revenue" as "revenue" | "expense",
    category: "",
    description: "",
    amount: "",
  });

  const { data: transactions = [], refetch } = trpc.transactions.list.useQuery();
  const createMutation = trpc.transactions.create.useMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await createMutation.mutateAsync({
        type: formData.type,
        category: formData.category,
        description: formData.description,
        amount: formData.amount,
      });
      
      setFormData({
        type: "revenue",
        category: "",
        description: "",
        amount: "",
      });
      setIsOpen(false);
      refetch();
    } catch (error) {
      console.error("Erro ao criar transação:", error);
    }
  };

  const revenues = transactions
    .filter(t => t.type === "revenue")
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);
  
  const expenses = transactions
    .filter(t => t.type === "expense")
    .reduce((sum, t) => sum + parseFloat(t.amount), 0);

  const profit = revenues - expenses;

  const revenueTransactions = transactions.filter(t => t.type === "revenue").sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  const expenseTransactions = transactions.filter(t => t.type === "expense").sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  const expenseCategories = ["Peças", "Combustível", "Aluguel", "Salários", "Utilidades", "Manutenção", "Outros"];
  const revenueCategories = ["Serviços", "Peças", "Outros"];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Financeiro</h1>
            <p className="text-slate-500 mt-2">Gestão de receitas e despesas</p>
          </div>
          <Dialog open={isOpen} onOpenChange={setIsOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => {
                setFormData({
                  type: "revenue",
                  category: "",
                  description: "",
                  amount: "",
                });
              }}>
                <Plus className="h-4 w-4 mr-2" />
                Nova Transação
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Nova Transação</DialogTitle>
                <DialogDescription>
                  Registre uma receita ou despesa
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="type">Tipo *</Label>
                  <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value as any, category: "" })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="revenue">Receita</SelectItem>
                      <SelectItem value="expense">Despesa</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="category">Categoria *</Label>
                  <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione uma categoria" />
                    </SelectTrigger>
                    <SelectContent>
                      {(formData.type === "revenue" ? revenueCategories : expenseCategories).map((cat) => (
                        <SelectItem key={cat} value={cat}>
                          {cat}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="description">Descrição</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>

                <div>
                  <Label htmlFor="amount">Valor *</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                    required
                  />
                </div>

                <Button type="submit" className="w-full">
                  Registrar Transação
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                Receitas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">R$ {revenues.toFixed(2)}</div>
              <p className="text-xs text-slate-500 mt-1">{revenueTransactions.length} transação{revenueTransactions.length !== 1 ? 's' : ''}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-red-600" />
                Despesas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">R$ {expenses.toFixed(2)}</div>
              <p className="text-xs text-slate-500 mt-1">{expenseTransactions.length} transação{expenseTransactions.length !== 1 ? 's' : ''}</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Lucro Líquido</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${profit >= 0 ? "text-green-600" : "text-red-600"}`}>
                R$ {profit.toFixed(2)}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {profit >= 0 ? "Lucro" : "Prejuízo"} no período
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Transactions List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Revenues */}
          <div>
            <h2 className="text-xl font-bold mb-4">Receitas</h2>
            {revenueTransactions.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-slate-500">Nenhuma receita registrada.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {revenueTransactions.map((transaction: any) => (
                  <Card key={transaction.id}>
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium">{transaction.category}</p>
                          {transaction.description && (
                            <p className="text-sm text-slate-600">{transaction.description}</p>
                          )}
                          <p className="text-xs text-slate-500 mt-1">
                            {new Date(transaction.createdAt).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-green-600">R$ {parseFloat(transaction.amount).toFixed(2)}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Expenses */}
          <div>
            <h2 className="text-xl font-bold mb-4">Despesas</h2>
            {expenseTransactions.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-slate-500">Nenhuma despesa registrada.</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {expenseTransactions.map((transaction: any) => (
                  <Card key={transaction.id}>
                    <CardContent className="pt-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium">{transaction.category}</p>
                          {transaction.description && (
                            <p className="text-sm text-slate-600">{transaction.description}</p>
                          )}
                          <p className="text-xs text-slate-500 mt-1">
                            {new Date(transaction.createdAt).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-red-600">R$ {parseFloat(transaction.amount).toFixed(2)}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
