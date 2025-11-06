CREATE TABLE `clients` (
	`id` int AUTO_INCREMENT NOT NULL,
	`name` varchar(255) NOT NULL,
	`email` varchar(320),
	`phone` varchar(20),
	`cpf` varchar(14),
	`address` text,
	`city` varchar(100),
	`state` varchar(2),
	`zipCode` varchar(10),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `clients_id` PRIMARY KEY(`id`),
	CONSTRAINT `clients_cpf_unique` UNIQUE(`cpf`)
);
--> statement-breakpoint
CREATE TABLE `serviceOrderItems` (
	`id` int AUTO_INCREMENT NOT NULL,
	`serviceOrderId` int NOT NULL,
	`description` varchar(255) NOT NULL,
	`type` enum('part','service') NOT NULL,
	`quantity` int NOT NULL DEFAULT 1,
	`unitCost` decimal(10,2) NOT NULL,
	`unitPrice` decimal(10,2) NOT NULL,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `serviceOrderItems_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `serviceOrders` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`vehicleId` int NOT NULL,
	`orderNumber` varchar(50) NOT NULL,
	`status` enum('pending','in_progress','completed','paid','cancelled') NOT NULL DEFAULT 'pending',
	`description` text,
	`totalCost` decimal(10,2) NOT NULL DEFAULT '0',
	`totalPrice` decimal(10,2) NOT NULL DEFAULT '0',
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	`completedAt` timestamp,
	`paidAt` timestamp,
	CONSTRAINT `serviceOrders_id` PRIMARY KEY(`id`),
	CONSTRAINT `serviceOrders_orderNumber_unique` UNIQUE(`orderNumber`)
);
--> statement-breakpoint
CREATE TABLE `transactions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`type` enum('revenue','expense') NOT NULL,
	`category` varchar(100) NOT NULL,
	`description` text,
	`amount` decimal(10,2) NOT NULL,
	`serviceOrderId` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `transactions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `vehicles` (
	`id` int AUTO_INCREMENT NOT NULL,
	`clientId` int NOT NULL,
	`brand` varchar(100) NOT NULL,
	`model` varchar(100) NOT NULL,
	`year` int,
	`licensePlate` varchar(10) NOT NULL,
	`vin` varchar(17),
	`color` varchar(50),
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	`updatedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `vehicles_id` PRIMARY KEY(`id`),
	CONSTRAINT `vehicles_licensePlate_unique` UNIQUE(`licensePlate`)
);
