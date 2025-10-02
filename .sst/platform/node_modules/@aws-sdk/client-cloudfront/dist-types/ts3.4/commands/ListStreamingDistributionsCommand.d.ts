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
  ListStreamingDistributionsRequest,
  ListStreamingDistributionsResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListStreamingDistributionsCommandInput
  extends ListStreamingDistributionsRequest {}
export interface ListStreamingDistributionsCommandOutput
  extends ListStreamingDistributionsResult,
    __MetadataBearer {}
export declare class ListStreamingDistributionsCommand extends $Command<
  ListStreamingDistributionsCommandInput,
  ListStreamingDistributionsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListStreamingDistributionsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListStreamingDistributionsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListStreamingDistributionsCommandInput,
    ListStreamingDistributionsCommandOutput
  >;
  private serialize;
  private deserialize;
}
