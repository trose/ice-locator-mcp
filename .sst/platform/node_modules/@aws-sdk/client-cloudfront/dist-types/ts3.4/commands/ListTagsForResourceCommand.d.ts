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
  ListTagsForResourceRequest,
  ListTagsForResourceResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListTagsForResourceCommandInput
  extends ListTagsForResourceRequest {}
export interface ListTagsForResourceCommandOutput
  extends ListTagsForResourceResult,
    __MetadataBearer {}
export declare class ListTagsForResourceCommand extends $Command<
  ListTagsForResourceCommandInput,
  ListTagsForResourceCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListTagsForResourceCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListTagsForResourceCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<ListTagsForResourceCommandInput, ListTagsForResourceCommandOutput>;
  private serialize;
  private deserialize;
}
