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
  ListRealtimeLogConfigsRequest,
  ListRealtimeLogConfigsResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListRealtimeLogConfigsCommandInput
  extends ListRealtimeLogConfigsRequest {}
export interface ListRealtimeLogConfigsCommandOutput
  extends ListRealtimeLogConfigsResult,
    __MetadataBearer {}
export declare class ListRealtimeLogConfigsCommand extends $Command<
  ListRealtimeLogConfigsCommandInput,
  ListRealtimeLogConfigsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListRealtimeLogConfigsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListRealtimeLogConfigsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListRealtimeLogConfigsCommandInput,
    ListRealtimeLogConfigsCommandOutput
  >;
  private serialize;
  private deserialize;
}
