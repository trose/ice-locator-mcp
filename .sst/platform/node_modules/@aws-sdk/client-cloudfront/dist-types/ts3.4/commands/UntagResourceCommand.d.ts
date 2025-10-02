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
import { UntagResourceRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UntagResourceCommandInput extends UntagResourceRequest {}
export interface UntagResourceCommandOutput extends __MetadataBearer {}
export declare class UntagResourceCommand extends $Command<
  UntagResourceCommandInput,
  UntagResourceCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UntagResourceCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UntagResourceCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<UntagResourceCommandInput, UntagResourceCommandOutput>;
  private serialize;
  private deserialize;
}
