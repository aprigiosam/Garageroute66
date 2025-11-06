import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { z } from "zod";
import * as db from "./db";
import { TRPCError } from "@trpc/server";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // ============ CLIENTS ============
  clients: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllClients();
    }),

    get: protectedProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ input }) => {
        const client = await db.getClientById(input.id);
        if (!client) {
          throw new TRPCError({ code: "NOT_FOUND", message: "Cliente não encontrado" });
        }
        return client;
      }),

    create: protectedProcedure
      .input(z.object({
        name: z.string().min(1),
        email: z.string().email().optional(),
        phone: z.string().optional(),
        cpf: z.string().optional(),
        address: z.string().optional(),
        city: z.string().optional(),
        state: z.string().optional(),
        zipCode: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        return await db.createClient(input);
      }),

    update: protectedProcedure
      .input(z.object({
        id: z.number(),
        name: z.string().optional(),
        email: z.string().email().optional(),
        phone: z.string().optional(),
        cpf: z.string().optional(),
        address: z.string().optional(),
        city: z.string().optional(),
        state: z.string().optional(),
        zipCode: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const { id, ...data } = input;
        return await db.updateClient(id, data);
      }),

    delete: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        return await db.deleteClient(input.id);
      }),
  }),

  // ============ VEHICLES ============
  vehicles: router({
    listByClient: protectedProcedure
      .input(z.object({ clientId: z.number() }))
      .query(async ({ input }) => {
        return await db.getVehiclesByClientId(input.clientId);
      }),

    get: protectedProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ input }) => {
        const vehicle = await db.getVehicleById(input.id);
        if (!vehicle) {
          throw new TRPCError({ code: "NOT_FOUND", message: "Veículo não encontrado" });
        }
        return vehicle;
      }),

    create: protectedProcedure
      .input(z.object({
        clientId: z.number(),
        brand: z.string().min(1),
        model: z.string().min(1),
        year: z.number().optional(),
        licensePlate: z.string().min(1),
        vin: z.string().optional(),
        color: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        return await db.createVehicle(input);
      }),

    update: protectedProcedure
      .input(z.object({
        id: z.number(),
        brand: z.string().optional(),
        model: z.string().optional(),
        year: z.number().optional(),
        licensePlate: z.string().optional(),
        vin: z.string().optional(),
        color: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const { id, ...data } = input;
        return await db.updateVehicle(id, data);
      }),

    delete: protectedProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        return await db.deleteVehicle(input.id);
      }),
  }),

  // ============ SERVICE ORDERS ============
  serviceOrders: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllServiceOrders();
    }),

    get: protectedProcedure
      .input(z.object({ id: z.number() }))
      .query(async ({ input }) => {
        const order = await db.getServiceOrderById(input.id);
        if (!order) {
          throw new TRPCError({ code: "NOT_FOUND", message: "Ordem de serviço não encontrada" });
        }
        return order;
      }),

    listByClient: protectedProcedure
      .input(z.object({ clientId: z.number() }))
      .query(async ({ input }) => {
        return await db.getServiceOrdersByClientId(input.clientId);
      }),

    create: protectedProcedure
      .input(z.object({
        clientId: z.number(),
        vehicleId: z.number(),
        orderNumber: z.string().min(1),
        description: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        return await db.createServiceOrder({
          ...input,
          status: "pending",
          totalCost: "0",
          totalPrice: "0",
        });
      }),

    updateStatus: protectedProcedure
      .input(z.object({
        id: z.number(),
        status: z.enum(["pending", "in_progress", "completed", "paid", "cancelled"]),
      }))
      .mutation(async ({ input }) => {
        const updateData: Record<string, any> = { status: input.status };
        if (input.status === "completed") {
          updateData.completedAt = new Date();
        }
        if (input.status === "paid") {
          updateData.paidAt = new Date();
        }
        return await db.updateServiceOrder(input.id, updateData);
      }),
  }),

  // ============ SERVICE ORDER ITEMS ============
  serviceOrderItems: router({
    list: protectedProcedure
      .input(z.object({ serviceOrderId: z.number() }))
      .query(async ({ input }) => {
        return await db.getServiceOrderItems(input.serviceOrderId);
      }),

    create: protectedProcedure
      .input(z.object({
        serviceOrderId: z.number(),
        description: z.string().min(1),
        type: z.enum(["part", "service"]),
        quantity: z.number().default(1),
        unitCost: z.string(),
        unitPrice: z.string(),
      }))
      .mutation(async ({ input }) => {
        const result = await db.createServiceOrderItem(input);
        
        // Update service order totals
        const items = await db.getServiceOrderItems(input.serviceOrderId);
        let totalCost = 0;
        let totalPrice = 0;
        
        items.forEach(item => {
          totalCost += parseFloat(item.unitCost) * item.quantity;
          totalPrice += parseFloat(item.unitPrice) * item.quantity;
        });
        
        await db.updateServiceOrder(input.serviceOrderId, {
          totalCost: totalCost.toString(),
          totalPrice: totalPrice.toString(),
        });
        
        return result;
      }),

    update: protectedProcedure
      .input(z.object({
        id: z.number(),
        serviceOrderId: z.number(),
        description: z.string().optional(),
        type: z.enum(["part", "service"]).optional(),
        quantity: z.number().optional(),
        unitCost: z.string().optional(),
        unitPrice: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const { id, serviceOrderId, ...data } = input;
        const result = await db.updateServiceOrderItem(id, data);
        
        // Update service order totals
        const items = await db.getServiceOrderItems(serviceOrderId);
        let totalCost = 0;
        let totalPrice = 0;
        
        items.forEach(item => {
          totalCost += parseFloat(item.unitCost) * item.quantity;
          totalPrice += parseFloat(item.unitPrice) * item.quantity;
        });
        
        await db.updateServiceOrder(serviceOrderId, {
          totalCost: totalCost.toString(),
          totalPrice: totalPrice.toString(),
        });
        
        return result;
      }),

    delete: protectedProcedure
      .input(z.object({ id: z.number(), serviceOrderId: z.number() }))
      .mutation(async ({ input }) => {
        const result = await db.deleteServiceOrderItem(input.id);
        
        // Update service order totals
        const items = await db.getServiceOrderItems(input.serviceOrderId);
        let totalCost = 0;
        let totalPrice = 0;
        
        items.forEach(item => {
          totalCost += parseFloat(item.unitCost) * item.quantity;
          totalPrice += parseFloat(item.unitPrice) * item.quantity;
        });
        
        await db.updateServiceOrder(input.serviceOrderId, {
          totalCost: totalCost.toString(),
          totalPrice: totalPrice.toString(),
        });
        
        return result;
      }),
  }),

  // ============ TRANSACTIONS ============
  transactions: router({
    list: protectedProcedure.query(async () => {
      return await db.getAllTransactions();
    }),

    create: protectedProcedure
      .input(z.object({
        type: z.enum(["revenue", "expense"]),
        category: z.string().min(1),
        description: z.string().optional(),
        amount: z.string(),
        serviceOrderId: z.number().optional(),
      }))
      .mutation(async ({ input }) => {
        return await db.createTransaction(input);
      }),
  }),
});

export type AppRouter = typeof appRouter;
