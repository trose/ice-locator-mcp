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
  PublishFunctionRequest,
  PublishFunctionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface PublishFunctionCommandInput extends PublishFunctionRequest {}
export interface PublishFunctionCommandOutput
  extends PublishFunctionResult,
    __MetadataBearer {}
export declare class PublishFunctionCommand extends $Command<
  PublishFunctionCommandInput,
  PublishFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: PublishFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: PublishFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<PublishFunctionCommandInput, PublishFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
