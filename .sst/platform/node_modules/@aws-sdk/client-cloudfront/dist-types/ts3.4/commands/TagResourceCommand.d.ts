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
import { TagResourceRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface TagResourceCommandInput extends TagResourceRequest {}
export interface TagResourceCommandOutput extends __MetadataBearer {}
export declare class TagResourceCommand extends $Command<
  TagResourceCommandInput,
  TagResourceCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: TagResourceCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: TagResourceCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<TagResourceCommandInput, TagResourceCommandOutput>;
  private serialize;
  private deserialize;
}
