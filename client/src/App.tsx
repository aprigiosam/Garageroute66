import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import Clients from "./pages/Clients";
import ClientDetail from "./pages/ClientDetail";
import ServiceOrders from "./pages/ServiceOrders";
import ServiceOrderDetail from "./pages/ServiceOrderDetail";
import Financial from "./pages/Financial";
import ClientQuote from "./pages/ClientQuote";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/clients"} component={Clients} />
      <Route path={"/clients/:id"} component={ClientDetail} />
      <Route path={"/service-orders"} component={ServiceOrders} />
      <Route path={"/service-orders/:id"} component={ServiceOrderDetail} />
      <Route path={"/financial"} component={Financial} />
      <Route path={"/quote/:id"} component={ClientQuote} />
      <Route path={"/404"} component={NotFound} />
      {/* Final fallback route */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
