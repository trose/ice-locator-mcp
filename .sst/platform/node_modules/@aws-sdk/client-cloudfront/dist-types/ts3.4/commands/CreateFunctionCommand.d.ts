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
  CreateFunctionRequest,
  CreateFunctionResult,
} from "../models/models_0";
export { __MetadataBearer, $Command };
export interface CreateFunctionCommandInput extends CreateFunctionRequest {}
export interface CreateFunctionCommandOutput
  extends CreateFunctionResult,
    __MetadataBearer {}
export declare class CreateFunctionCommand extends $Command<
  CreateFunctionCommandInput,
  CreateFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<CreateFunctionCommandInput, CreateFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
