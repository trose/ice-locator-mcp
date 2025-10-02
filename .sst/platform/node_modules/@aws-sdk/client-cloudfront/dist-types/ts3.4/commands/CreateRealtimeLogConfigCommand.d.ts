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
  CreateRealtimeLogConfigRequest,
  CreateRealtimeLogConfigResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateRealtimeLogConfigCommandInput
  extends CreateRealtimeLogConfigRequest {}
export interface CreateRealtimeLogConfigCommandOutput
  extends CreateRealtimeLogConfigResult,
    __MetadataBearer {}
export declare class CreateRealtimeLogConfigCommand extends $Command<
  CreateRealtimeLogConfigCommandInput,
  CreateRealtimeLogConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateRealtimeLogConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateRealtimeLogConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateRealtimeLogConfigCommandInput,
    CreateRealtimeLogConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
