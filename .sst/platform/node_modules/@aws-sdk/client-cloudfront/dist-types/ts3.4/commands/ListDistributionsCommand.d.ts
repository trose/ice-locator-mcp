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
  ListDistributionsRequest,
  ListDistributionsResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsCommandInput
  extends ListDistributionsRequest {}
export interface ListDistributionsCommandOutput
  extends ListDistributionsResult,
    __MetadataBearer {}
export declare class ListDistributionsCommand extends $Command<
  ListDistributionsCommandInput,
  ListDistributionsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListDistributionsCommandInput, ListDistributionsCommandOutput>;
  private serialize;
  private deserialize;
}
