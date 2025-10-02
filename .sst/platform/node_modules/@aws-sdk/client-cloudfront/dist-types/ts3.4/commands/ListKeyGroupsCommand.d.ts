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
import { ListKeyGroupsRequest, ListKeyGroupsResult } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListKeyGroupsCommandInput extends ListKeyGroupsRequest {}
export interface ListKeyGroupsCommandOutput
  extends ListKeyGroupsResult,
    __MetadataBearer {}
export declare class ListKeyGroupsCommand extends $Command<
  ListKeyGroupsCommandInput,
  ListKeyGroupsCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListKeyGroupsCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListKeyGroupsCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListKeyGroupsCommandInput, ListKeyGroupsCommandOutput>;
  private serialize;
  private deserialize;
}
