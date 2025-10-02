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
  ListDistributionsByRealtimeLogConfigRequest,
  ListDistributionsByRealtimeLogConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsByRealtimeLogConfigCommandInput
  extends ListDistributionsByRealtimeLogConfigRequest {}
export interface ListDistributionsByRealtimeLogConfigCommandOutput
  extends ListDistributionsByRealtimeLogConfigResult,
    __MetadataBearer {}
export declare class ListDistributionsByRealtimeLogConfigCommand extends $Command<
  ListDistributionsByRealtimeLogConfigCommandInput,
  ListDistributionsByRealtimeLogConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsByRealtimeLogConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsByRealtimeLogConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListDistributionsByRealtimeLogConfigCommandInput,
    ListDistributionsByRealtimeLogConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
