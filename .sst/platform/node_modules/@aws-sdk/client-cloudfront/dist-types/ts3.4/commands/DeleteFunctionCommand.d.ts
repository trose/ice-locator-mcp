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
import { DeleteFunctionRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteFunctionCommandInput extends DeleteFunctionRequest {}
export interface DeleteFunctionCommandOutput extends __MetadataBearer {}
export declare class DeleteFunctionCommand extends $Command<
  DeleteFunctionCommandInput,
  DeleteFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<DeleteFunctionCommandInput, DeleteFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
