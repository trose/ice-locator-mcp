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
import { DeletePublicKeyRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeletePublicKeyCommandInput extends DeletePublicKeyRequest {}
export interface DeletePublicKeyCommandOutput extends __MetadataBearer {}
export declare class DeletePublicKeyCommand extends $Command<
  DeletePublicKeyCommandInput,
  DeletePublicKeyCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeletePublicKeyCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeletePublicKeyCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<DeletePublicKeyCommandInput, DeletePublicKeyCommandOutput>;
  private serialize;
  private deserialize;
}
