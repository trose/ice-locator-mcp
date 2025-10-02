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
import { DeleteKeyGroupRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteKeyGroupCommandInput extends DeleteKeyGroupRequest {}
export interface DeleteKeyGroupCommandOutput extends __MetadataBearer {}
export declare class DeleteKeyGroupCommand extends $Command<
  DeleteKeyGroupCommandInput,
  DeleteKeyGroupCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteKeyGroupCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteKeyGroupCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<DeleteKeyGroupCommandInput, DeleteKeyGroupCommandOutput>;
  private serialize;
  private deserialize;
}
