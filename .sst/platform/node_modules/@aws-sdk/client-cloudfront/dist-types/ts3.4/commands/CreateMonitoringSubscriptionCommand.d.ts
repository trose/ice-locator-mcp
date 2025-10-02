import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  CreateMonitoringSubscriptionRequest,
  CreateMonitoringSubscriptionResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateMonitoringSubscriptionCommandInput
  extends CreateMonitoringSubscriptionRequest {}
export interface CreateMonitoringSubscriptionCommandOutput
  extends CreateMonitoringSubscriptionResult,
    __MetadataBearer {}
export declare class CreateMonitoringSubscriptionCommand extends $Command<
  CreateMonitoringSubscriptionCommandInput,
  CreateMonitoringSubscriptionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateMonitoringSubscriptionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateMonitoringSubscriptionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateMonitoringSubscriptionCommandInput,
    CreateMonitoringSubscriptionCommandOutput
  >;
  private serialize;
  private deserialize;
}
