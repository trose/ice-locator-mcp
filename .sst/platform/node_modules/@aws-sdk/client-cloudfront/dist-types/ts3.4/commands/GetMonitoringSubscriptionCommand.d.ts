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
  GetMonitoringSubscriptionRequest,
  GetMonitoringSubscriptionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetMonitoringSubscriptionCommandInput
  extends GetMonitoringSubscriptionRequest {}
export interface GetMonitoringSubscriptionCommandOutput
  extends GetMonitoringSubscriptionResult,
    __MetadataBearer {}
export declare class GetMonitoringSubscriptionCommand extends $Command<
  GetMonitoringSubscriptionCommandInput,
  GetMonitoringSubscriptionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetMonitoringSubscriptionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetMonitoringSubscriptionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetMonitoringSubscriptionCommandInput,
    GetMonitoringSubscriptionCommandOutput
  >;
  private serialize;
  private deserialize;
}
