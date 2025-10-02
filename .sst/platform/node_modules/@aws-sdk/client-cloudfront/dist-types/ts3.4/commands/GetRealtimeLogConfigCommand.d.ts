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
  GetRealtimeLogConfigRequest,
  GetRealtimeLogConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetRealtimeLogConfigCommandInput
  extends GetRealtimeLogConfigRequest {}
export interface GetRealtimeLogConfigCommandOutput
  extends GetRealtimeLogConfigResult,
    __MetadataBearer {}
export declare class GetRealtimeLogConfigCommand extends $Command<
  GetRealtimeLogConfigCommandInput,
  GetRealtimeLogConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetRealtimeLogConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetRealtimeLogConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetRealtimeLogConfigCommandInput,
    GetRealtimeLogConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
