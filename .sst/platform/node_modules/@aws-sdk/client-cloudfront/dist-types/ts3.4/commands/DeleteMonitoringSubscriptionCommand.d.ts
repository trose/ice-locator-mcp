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
  DeleteMonitoringSubscriptionRequest,
  DeleteMonitoringSubscriptionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteMonitoringSubscriptionCommandInput
  extends DeleteMonitoringSubscriptionRequest {}
export interface DeleteMonitoringSubscriptionCommandOutput
  extends DeleteMonitoringSubscriptionResult,
    __MetadataBearer {}
export declare class DeleteMonitoringSubscriptionCommand extends $Command<
  DeleteMonitoringSubscriptionCommandInput,
  DeleteMonitoringSubscriptionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteMonitoringSubscriptionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteMonitoringSubscriptionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteMonitoringSubscriptionCommandInput,
    DeleteMonitoringSubscriptionCommandOutput
  >;
  private serialize;
  private deserialize;
}
