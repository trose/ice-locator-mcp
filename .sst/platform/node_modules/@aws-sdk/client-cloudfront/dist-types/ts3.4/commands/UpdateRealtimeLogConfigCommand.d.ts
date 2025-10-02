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
  UpdateRealtimeLogConfigRequest,
  UpdateRealtimeLogConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateRealtimeLogConfigCommandInput
  extends UpdateRealtimeLogConfigRequest {}
export interface UpdateRealtimeLogConfigCommandOutput
  extends UpdateRealtimeLogConfigResult,
    __MetadataBearer {}
export declare class UpdateRealtimeLogConfigCommand extends $Command<
  UpdateRealtimeLogConfigCommandInput,
  UpdateRealtimeLogConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateRealtimeLogConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateRealtimeLogConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateRealtimeLogConfigCommandInput,
    UpdateRealtimeLogConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
