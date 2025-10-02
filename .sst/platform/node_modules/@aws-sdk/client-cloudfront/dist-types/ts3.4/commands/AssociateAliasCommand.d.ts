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
import { AssociateAliasRequest } from "../models/models_0";
export { __MetadataBearer, $Command };
export interface AssociateAliasCommandInput extends AssociateAliasRequest {}
export interface AssociateAliasCommandOutput extends __MetadataBearer {}
export declare class AssociateAliasCommand extends $Command<
  AssociateAliasCommandInput,
  AssociateAliasCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: AssociateAliasCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: AssociateAliasCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<AssociateAliasCommandInput, AssociateAliasCommandOutput>;
  private serialize;
  private deserialize;
}
