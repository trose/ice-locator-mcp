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
import { DeleteRealtimeLogConfigRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteRealtimeLogConfigCommandInput
  extends DeleteRealtimeLogConfigRequest {}
export interface DeleteRealtimeLogConfigCommandOutput
  extends __MetadataBearer {}
export declare class DeleteRealtimeLogConfigCommand extends $Command<
  DeleteRealtimeLogConfigCommandInput,
  DeleteRealtimeLogConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteRealtimeLogConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteRealtimeLogConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteRealtimeLogConfigCommandInput,
    DeleteRealtimeLogConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
