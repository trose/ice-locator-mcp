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
import { ListFunctionsRequest, ListFunctionsResult } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListFunctionsCommandInput extends ListFunctionsRequest {}
export interface ListFunctionsCommandOutput
  extends ListFunctionsResult,
    __MetadataBearer {}
export declare class ListFunctionsCommand extends $Command<
  ListFunctionsCommandInput,
  ListFunctionsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListFunctionsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListFunctionsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListFunctionsCommandInput, ListFunctionsCommandOutput>;
  private serialize;
  private deserialize;
}
