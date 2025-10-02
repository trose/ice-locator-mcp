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
  UpdateFunctionRequest,
  UpdateFunctionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateFunctionCommandInput extends UpdateFunctionRequest {}
export interface UpdateFunctionCommandOutput
  extends UpdateFunctionResult,
    __MetadataBearer {}
export declare class UpdateFunctionCommand extends $Command<
  UpdateFunctionCommandInput,
  UpdateFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<UpdateFunctionCommandInput, UpdateFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
